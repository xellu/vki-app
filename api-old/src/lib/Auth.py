from nautica.api.http import Context
from nautica.api import Sessions
from .Users import UserManager

from src.lib.Language import Messages

class AuthResponse:
    def __init__(self, ok: bool, error: str | None = None, userId: str | None = None):
        self.ok = ok
        self.error = error
        
        self.userId = userId

    def getUser(self) -> UserManager:
        return UserManager(uid=self.userId)

class Authenticate:
    def __init__(self, ctx: Context):
        self.ctx = ctx
        
    def cookie(self, cookie_name="session") -> AuthResponse:
        sessionId = self.ctx.args.cookies.get(cookie_name)
        if not sessionId:
            return AuthResponse(False, error=Messages.AUTH_CANT_GET_SESSION.value)
        
        userId = Sessions.get(sessionId)
        if not userId:
            return AuthResponse(False, error=Messages.AUTH_EXPIRED_SESSION.value)
        
        return AuthResponse(True, userId=userId)
    
    def header(self, header_name="Authorization") -> AuthResponse:
        sessionId = self.ctx.args.headers.get(header_name)
        if not sessionId:
            return AuthResponse(False, error=Messages.AUTH_CANT_GET_SESSION.value)
        
        userId = Sessions.get(sessionId)
        if not userId:
            return AuthResponse(False, error=Messages.AUTH_EXPIRED_SESSION.value)
        
        return AuthResponse(True, userId=userId)