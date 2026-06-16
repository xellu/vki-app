NAuthPreset = """
from nautica import Services
from plugins.nauth import NAuth, NAuthSession

Auth: NAuth = Services.get("NAuth")
# Usage:
# from src.nauth import Auth
# @Auth.Protect() <- on a route you want protected by auth

# Define a profile getter
def profile_getter(session: NAuthSession):
    return {
        #define your profile object here
    }
    #output of this function will be available in the request handler as 'ctx.profile' <- this can be anything: dict, user manager, etc.

# Configure the Auth
Auth.Configure() \\
    .setProfileGetter(profile_getter) \\
    .addCookieKey("session") \\
    .addHeaderKey("Authorization")
"""
