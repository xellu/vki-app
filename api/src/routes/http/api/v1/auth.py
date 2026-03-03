from nautica.api.http import (
    Context,
    
    Request,
    Require,
    
    Reply,
    Error
)
from nautica.api import Sessions

from src.lib.Users import UserManager
from src.lib.Auth import Authenticate
from src.lib.NsuAPI import NsuAPI

from fastapi.responses import JSONResponse

@Request.POST()
@Require.body(email=str, password=str)
async def login(ctx: Context):
    user = UserManager(email=ctx.body["email"])
    
    #check if cab.nsu.ru login is valid
    cookies, error = await NsuAPI.login(ctx.body["email"], ctx.body["password"])
    if error:
        return Error(error), 403
    
    _isNew = False
    if not user.is_valid(): #create new user
        user.create(ctx.body["email"], ctx.body["password"])
        _isNew = True
    
    if _isNew or not user.get("name") or not user.get("group"): #or True: #get profile data only on sign up or if they're missing for some reason
        #update profile name and group
        name, group = NsuAPI(cookies).get_profile()
        if name: user.user["name"] = name
        if group: user.user["group"] = group
        if name or group:
            user.update()
    
    if ctx.body["password"] != user.decrypt_password(): #update password, if a user changed it
        user.user["password"] = user.encrypt_password(ctx.body["password"])
        user.update()
    
    #create session    
    sessionId = Sessions.create(
        refId = user.get("_id"),
        expire = None # so sessions won't expire
    )
    
    r = JSONResponse(content={"session": sessionId})
    r.set_cookie("session", sessionId, max_age=60*60*24*365)
    return r

@Request.POST() #apparently POST instead of GET prevents caching issues????
async def me(ctx: Context):
    auth = Authenticate(ctx).cookie()
    if not auth.ok: return Error(auth.error), 401
    
    user = auth.getUser()
    return Reply(
        **user.get_profile()
    )
    
@Request.POST()
async def logout(ctx: Context):
    auth = Authenticate(ctx).cookie()
    if not auth.ok: return Error(auth.error), 401
    
    Sessions.delete(ctx.cookies.get("session"))
    return Reply()