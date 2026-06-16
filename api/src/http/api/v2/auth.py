from napi.http import (
    HTTP,
    Context,
    
    Reply,
    Error
)

from src.nauth import Auth
from src.lib.Users import UserManager
from src.lib.NsuAPI import NsuAPI

import time

@HTTP.POST()
@HTTP.Require(body={ "email": str, "password": str })
async def login(ctx: Context):
    if not ctx.body["email"].endswith("@g.nsu.ru"):
        ctx.body["email"] += "@g.nsu.ru" #to prevent using username logins
    
    user = UserManager(email=ctx.body["email"])
    
    #check if cab.nsu.ru login is valid
    cookies, error = await NsuAPI.Client.login(ctx.body["email"], ctx.body["password"])
    if error:
        # return Error(error), 403
        raise Error(403)
    
    _isNew = False
    if not user.is_valid(): #create new user
        user.create(ctx.body["email"], ctx.body["password"])
        _isNew = True
    
    if _isNew or not user.get("name") or not user.get("group"): #or True: #get profile data only on sign up or if they're missing for some reason
        #update profile name and group
        name, group = NsuAPI.getClient(cookies).get_profile()
        if name: user.user["name"] = name
        if group: user.user["group"] = group
        if name or group:
            user.update()
    
    if ctx.body["password"] != user.decrypt_password(): #update password, if a user changed it
        user.user["password"] = user.encrypt_password(ctx.body["password"])
        user.update()
    
    #create session
    expire = 60 * 60 * 24 * 365
    session = Auth.createSession(
        refId = user.get("_id"),
        expire = time.time() + expire
    )

    return Reply(session=session.sessionId) \
        .SetCookie("session") \
            .value(session.sessionId) \
            .maxAge(expire) \
            .build()
            
@HTTP.POST()
@Auth.Protect()
async def me(ctx: Context):
    user: UserManager = ctx.profile
    
    return Reply(
        **user.get_profile()
    )
    
@HTTP.POST()
@HTTP.Require(cookies={"session": str})
async def logout(ctx: Context):
    Auth.deleteSession(ctx.cookies.get("session"))
    return Reply()