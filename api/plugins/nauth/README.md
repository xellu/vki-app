# NAuth
*aka NauticaAuth*


NAuth is a simple and configurable session manager built on top of MongoDB.

## Usage
### Setup
After installation, a file named `src/nauth/__init__.py` will be available. Edit this file to configure the auth plugin.

To start configuring the auth, you'll need to get `NAuthConfig` first. To do that, use `Configure()` method:

```py
from nautica import Services
from plugins.nauth import NAuth

Auth: NAuth = Services.get("NAuth")
Auth.Configure() \
    .addCookieKey("session") #will search for a session cookie
```

### Profile Getter
The Auth automatically injects `profile` into `Context`:

```py
from napi.http import Context
from src.nauth import Auth

@HTTP.GET()
@Auth.Protect()
def protected_resource(ctx: Context):
    print(ctx.profile) #<-- Your data
```

For this to work, you'll need to set up a profile getter:

```py
Auth.Configure() \
    .addCookieKey("session") \
    .setProfileGetter(profile_getter)
```

The profile getter takes in a session parameter (of type `NAuthSession`), and can return anything:
```py
def profile_getter(session: NAuthSession):
    return {
        #define your profile object here
    }
    #output of this function will be available in the request handler as 'ctx.profile' <- this can be anything: dict, user manager, etc.
```

### Search Parameters
The plugin automatically searches for cookies and headers in the request. If none are found, it'll automatically cancel the request before reaching your handler. To define cookies and header keys to search for use `addCookieKey` and `addHeaderKey`:

```py
Auth.Configure() \
    .addCookieKey("session") \
    .addHeaderKey("Authorization") \
    .addHeaderKey("Authorization2") # Can search for multiple keys at once    
```
*If either one is present, the request will go through. (provided the session is valid)*

### Creating and Deleting Sessions
You'll need to create sessions manually, for example in login requests.

```py
import time
from src.nauth import Auth

session = Auth.createSession("user-123", expire = time.time() + 24 * 60 * 60)
                              # ^                  ^- Timestamp, until when the session is valid.
                              # |- Reference ID, use this to load account data in the profile getter
```
Set expire to `None` for a permanent session

To delete a session you can use 2 methods:

1. Delete a single session
```py
session_id = ...
Auth.deleteSession(session_id)
```

2. Delete all user's sessions
```py
ref_id = ...
Auth.deleteMany(ref_id)
```

Expired sessions are deleted automatically.

## Auth Example

This code following code is from this website, available at https://github.com/xellu/nautica-package-manager/tree/main/api/src

### src/nauth/__init__.py

```py
from nautica import Services
from plugins.auth import NAuth, NAuthSession
from src.lib.User import User

Auth: NAuth = Services.get("NAuth")
# Usage:
# from src.nauth import Auth
# @Auth.Protect() <- on a route you want protected by auth

# Define a profile getter
def profile_getter(session: NAuthSession):
    return User(session.refId)

# Configure the Auth
Auth.Configure() \
    .setProfileGetter(profile_getter) \
    .addCookieKey("session") \
    .addHeaderKey("Authorization")
```
https://github.com/xellu/nautica-package-manager/blob/main/api/src/nauth/__init__.py


### src/lib/User.py

```py
from nautica import Services
from nautica.ext.Util import hashStr
from napi.http import Error

import secrets

def UserTemplate():
    return {
        "userId": f"usr_{secrets.token_hex(16)}",
        "username": None,
        "password": None
    }

class User:
    def __init__(self, _id: str = None, _user: dict = None):
        self._id = _id or _user.get("userId")
        
        self._user = _user or Services["MongoDB"]("napm_users").find_one({"userId": _id})
        if not self._user:
            raise Error(500, "Account not found", details={"exception": f"Profile with id '{_id}' does not exist"})
    
    @staticmethod
    def create(username, password):
        ...
    
    @staticmethod
    def getByUsername(username: str):
        ...
    
    def verify(self, password: str) -> bool:
        return self._user["password"] == hashStr(f"{self._id}${password}")
    
    def __getitem__(self, key):
        ...
    
    def __setitem__(self, key, value):
        ...

    def toDict(self):
        ...

```
Full code available here:
https://github.com/xellu/nautica-package-manager/blob/main/api/src/lib/User.py


See how login works:
https://github.com/xellu/nautica-package-manager/blob/main/api/src/http/api/v1/auth.py