import time
import asyncio

from nautica.api.http import (
    Context,
    Request,
    Require,

    Reply,
    ReplyList,
    Error,
)
from nautica.api import Config

from fastapi.responses import JSONResponse

from src.lib.NsuAPI import NsuAPI
from src.lib.Auth import Authenticate
from src.lib.grades.Worker import GradesCache, Worker

@Request.GET()
@Require.query(semester=str) #query args can't be anything other than a string :pensive:
async def grades(ctx: Context):
    auth = Authenticate(ctx).cookie()
    if not auth.ok: return Error(auth.error), 401

    user = auth.getUser()
    semester = int(ctx.query["semester"])
    interval = Config("vki")["grades.updateInterval"]

    cached = GradesCache.getByKey(f"{user.uid}_sem{semester}")
    if cached and cached.get("semester") == semester:
        latest_meta = GradesCache.getByKey(f"{user.uid}_latest")
        is_latest = not latest_meta or latest_meta.get("semester") == semester

        if is_latest:
            age = time.time() - cached.get("fetchedAt", 0)
            if age >= interval:
                asyncio.create_task(Worker.refresh_user(user.get()))
                update_in = 30
            else:
                update_in = max(0, int(interval - age))
        else:
            update_in = None  # older semester, grades won't change

        return JSONResponse(content={"grades": cached["grades"], "update_in": update_in})

    #fetch synchronously on first visit
    cookies, error = await NsuAPI.login(user.get("email"), user.decrypt_password())
    if error:
        return Error(error), 500

    api = NsuAPI(cookies)
    grades = await api.get_grades(semester)
    latest_sem = await api.get_latest_semester()
    serialized = [g.to_dict() for g in grades]

    GradesCache.create(userId=f"{user.uid}_sem{semester}", semester=semester, grades=serialized, fetchedAt=time.time())

    latest_key = f"{user.uid}_latest"
    if GradesCache.getByKey(latest_key):
        GradesCache.setByKey(latest_key, "semester", latest_sem)
    else:
        GradesCache.create(userId=latest_key, semester=latest_sem)

    return JSONResponse(content={"grades": serialized, "update_in": interval if semester == latest_sem else None})
