from nautica.api.http import (
    Context,
    
    Request,
    Require,
    
    Reply,
    Error
)

@Request.POST()
@Require.body(username=str, password=str)
def login(ctx: Context):
    pass

@Request.GET()
def me(ctx: Context):
    pass