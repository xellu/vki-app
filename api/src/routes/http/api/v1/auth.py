from nautica.api.http import (
    Context,
    
    Request,
    Require,
    
    Reply,
    Error
)
from src.lib.Users import UserManager
from src.lib.NsuAPI import NsuAPI

@Request.POST()
@Require.body(email=str, password=str)
async def login(ctx: Context):
    user = UserManager(email=ctx.body["email"])
    
    if not user.is_valid(): #create new user
        #check if cab.nsu.ru login is valid
        _, error = NsuAPI.login(ctx.body["email"], ctx.body["password"])
        if error:
            return Error(error), 403
        
        user.create(ctx.body["email"], ctx.body["password"])
        
    #return user data
    return Reply(
        **user.get_profile()
    )

@Request.GET()
async def me(ctx: Context):
    pass