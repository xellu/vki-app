import secrets

class NAuthConfig:
    """
    Fluent configuration object for NAuth
    Use to define where to look for session tokens and how to resolve a user profile.
    """

    def __init__(self):
        self.headerSearchFor: set[str] = set()
        self.cookieSearchFor: set[str] = set()
        self.profileGetter: callable | None = None

    def addHeaderKey(self, key: str):
        """Register a request header name to search for a session token."""
        self.headerSearchFor.add(key)
        return self

    def addCookieKey(self, key: str):
        """Register a cookie name to search for a session token."""
        self.cookieSearchFor.add(key)
        return self

    def setProfileGetter(self, func: callable):
        """Set the callable used to resolve a user profile from a session document. Its return value is attached to ctx.profile."""
        self.profileGetter = func
        return self
    
class NAuthSession:
    def __init__(self, sessionId: str = None, refId: str = None, expire: float | None = None):
        """
        :param sessionId: Unique session token; auto-generated if omitted.
        :param refId: Caller-defined reference (e.g. user ID) tied to this session.
        :param expire: Unix timestamp after which the session is invalid; defaults to permanent.
        """
        self.sessionId = sessionId or secrets.token_hex(32)
        self.refId = refId
        self.expire: float | None = expire

    def toDict(self) -> dict:
        return {"sessionId": self.sessionId, "refId": self.refId, "expire": self.expire}
        