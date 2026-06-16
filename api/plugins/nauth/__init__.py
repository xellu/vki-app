from nautica import Service, Config, ConfigBuilder, Logger, Services
from nautica.ext.Util import maybeAwait
from nautica.ext.Path import getRoot
from napi.http import Context, HTTP, Error, StatusCodes

from .static import NAuthPreset
from .models import NAuthConfig, NAuthSession

import os
import time

class NAuth(Service):
    def __init__(self):
        super().__init__()
        self.config: NAuthConfig = NAuthConfig()
        
        self.nextClean = 0

    def onStart(self, registry):
        if not os.path.exists(getRoot("src", "nauth", "__init__.py")):
            with open(getRoot("src", "nauth", "__init__.py"), "w") as f: f.write(NAuthPreset)
            
    def onClose(self, reason):
        pass

    def Protect(self):
        """Decorator that gates a route behind session authentication when NAuth is enabled."""
        def decorator(func):
            if self.isEnabled():
                HTTP.Before(func)(self.handleRequest)
            return func
        return decorator

    def Configure(self):
        """Return the mutable NAuthConfig for fluent configuration chaining."""
        return self.config
    
    def createSession(self, refId: str, expire: float | None) -> NAuthSession:
        """
        Create a new session
        
        :refId: A reference ID - use this to define for example user ID
        :expire: When to expire - Timestamp or None to never expire
        """
        s = NAuthSession(refId = refId, expire = expire)
        Services["MongoDB"]("nauth_sessions").insert_one(s.toDict())
        
        return s
        
    def deleteSession(self, sessionId: str):
        """Delete a single session by its session token."""
        Services["MongoDB"]("nauth_sessions").delete_one({"sessionId": sessionId})

    def deleteMany(self, refId: str):
        """Delete all sessions associated with the given refId (e.g. when a user logs out everywhere)."""
        Services["MongoDB"]("nauth_sessions").delete_many({"refId": refId})

    def deleteExpired(self):
        """Deletes all sessions that have already expired."""
        Services["MongoDB"]("nauth_sessions").delete_many({"expire": {"$ne": None, "$lt": time.time()}})
        Logger.info("Deleted expired sessions")

    async def handleRequest(self, ctx: Context, *args, **kwargs):
        sessionId: str | None = None
        
        if time.time() > self.nextClean:
            self.deleteExpired()
            self.nextClean = time.time() + 60 * 60
        
        for key in self.config.headerSearchFor:
            if key in ctx.headers:
                sessionId = ctx.headers[key]
                break
            
        if not sessionId:
            for key in self.config.cookieSearchFor:
                if key in ctx.cookies:
                    sessionId = ctx.cookies[key]
                    break
                
        if not sessionId:
            raise Error(StatusCodes.UNAUTHORIZED, "No session provided", details={
                "exception": "Expected a header or cookie with session, got none"
            })
            
        s = Services["MongoDB"]("nauth_sessions").find_one({"sessionId": sessionId})
        if not s:
            raise Error(StatusCodes.UNAUTHORIZED, "Unknown session")
            
        if s["expire"] and s["expire"] < time.time():
            Services["MongoDB"]("nauth_sessions").delete_one({"sessionId": sessionId})
            raise Error(StatusCodes.UNAUTHORIZED, "Session expired")
        
        if not self.config.profileGetter:
            return
        
        try:
            profile = await maybeAwait(self.config.profileGetter(
                NAuthSession(s["sessionId"], s["refId"], s["expire"])
            ))
            setattr(ctx, "profile", profile)
        except Exception as e:
            Logger.trace(e)
            raise Error(StatusCodes.INTERNAL_SERVER_ERROR, "Unable to retrieve profile data", details={
                "exception": str(e)
            })    
    
Service.Export(
    NAuth,
    srcDir="nauth",
    depends_on = ["MongoDB"]
)