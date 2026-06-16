import time
import asyncio

from napi.http import (
    HTTP,
    Context,
    Reply,
    Error
)

from nautica import Services, Config

from src.nauth import Auth
from src.lib.Users import UserManager
from src.lib.NsuAPI import NsuAPI

from plugins.GradesWorker import GradesWorker

@HTTP.GET()
@HTTP.Require(query={"semester": int})
@Auth.Protect()
async def grades(ctx: Context):
    user: UserManager = ctx.profile
    
    interval = Config("vki")["grades.updateInterval"]
    semester = ctx.query["semester"]

    worker: GradesWorker = Services.get("GradesWorker")
    GradesCache = worker.gradesCache
    
    cached = GradesCache.getByKey(f"{user.uid}_sem{semester}")
    if cached and cached.get("semester") == semester:
        latest_meta = GradesCache.getByKey(f"{user.uid}_latest")
        is_latest = not latest_meta or latest_meta.get("semester") == semester

        if is_latest:
            age = time.time() - cached.get("fetchedAt", 0)
            if age >= interval:
                asyncio.create_task(worker.refresh_user(user.get()))
                update_in = 30
            else:
                update_in = max(0, int(interval - age))
        else:
            update_in = None  # older semester, grades won't change

        # return JSONResponse(content={"grades": cached["grades"], "update_in": update_in})
        return Reply(
            grades = cached["grades"],
            update_in = update_in
        )

    #fetch synchronously on first visit
    cookies, error = await NsuAPI.Client.login(user.get("email"), user.decrypt_password())
    if error:
        # return Error(error), 500
        raise Error(500, error)

    api = NsuAPI.getClient(cookies)
    
    grades = await api.get_grades(semester)
    latest_sem = await api.get_latest_semester()
    serialized = [g.to_dict() for g in grades]

    userKey = f"{user.uid}_sem{semester}"
    if not GradesCache.getByKey(userKey):
        GradesCache.create(userId=userKey, semester=semester, grades=serialized, fetchedAt=time.time())

    latest_key = f"{user.uid}_latest"
    if GradesCache.getByKey(latest_key):
        GradesCache.setByKey(latest_key, "semester", latest_sem)
    else:
        GradesCache.create(userId=latest_key, semester=latest_sem)

    # return JSONResponse(content={"grades": serialized, "update_in": interval if semester == latest_sem else None})
    return Reply(
        grades = serialized,
        update_in = interval if semester == latest_sem else None
    )
    
@HTTP.GET()
@Auth.Protect()
async def semesters(ctx: Context):
    user: UserManager = ctx.profile
    
    GradesCache: GradesWorker = Services.get("GradesWorker").gradesCache
    
    cached = GradesCache.getByKey(f"{user.uid}_latest")
    if cached and cached.get("semester"):
        return Reply(last=cached["semester"])

    cookies, error = await NsuAPI.Client.login(user.get("email"), user.decrypt_password())
    if error:
        return Error(error), 500

    api = NsuAPI.getClient(cookies)
    last = await api.get_latest_semester()

    GradesCache.create(userId=f"{user.uid}_latest", semester=last)

    return Reply(last=last)