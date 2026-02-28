from .models.User import UserModel, SanitizeUser

from nautica.services.logger import LogManager
from nautica.api import MongoDB

# from plugins.intercom import Intercom

logger = LogManager("Lib.Users")

class UserActionResponse:
    def __init__(self, ok: bool, error: str | None = None, meta: any = None):
        self.ok = ok
        self.error = error
        self.meta = meta

class UserManager:
    def __init__(self, uid = None, email = None, _data: dict = None):
        """
        A class to manage user accounts.
        
        Parameters:
            uid (str): User ID of the user.
            email (str): User login
        
        Raises:
            ValueError: If neither discord nor minecraft is provided.
        """
        
        self.uid = uid
        self.email = email
        
        self.user = _data or None
        
        if not uid and not email and not _data:
            raise ValueError("User ID, Discord ID or Minecraft username must be provided")
        
        self.load()
        
    def is_valid(self):
        """Check if the user is valid."""
        return self.user is not None
    
    def load(self):
        if self.uid:
            self.user = MongoDB("vki").users.find_one({"_id": self.uid})
        elif self.email:
            self.user = MongoDB("vki").users.find_one({"email": self.email})
            
    
        if self.user:
            self.uid = self.user["_id"]
            self.email = self.user["email"]
    
    def update(self):
        """Update the user in the database."""
        if not self.is_valid():
            return UserActionResponse(False, "User not found")
        
        MongoDB("vki").users.update_one({"_id": self.uid}, {"$set": self.user})        
        
        return UserActionResponse(True)
    
    def get(self, key: str = None, fallback = None):
        if not key:            
            return self.user
        return self.user.get(key, fallback)

    def get_profile(self):
        return SanitizeUser(self.user.copy())

    def delete(self):
        """Delete the user."""
        if not self.is_valid():
            return UserActionResponse(False, "User not found")
        
        #TODO: remove all roles
        
        MongoDB("vki").users.delete_one({"_id": self.uid})
        self.user = None
        
        return UserActionResponse(True)
    
    def create(self, email = None, password = None):
        """Create a new user."""
        if self.is_valid():
            return UserActionResponse(False, "User already exists")
        
        self.user = UserModel()
        if not email and not password:
            return UserActionResponse(False, "Email or password is missing")
        
        self.user["email"] = email
        self.user["password"]
        
        MongoDB("vki").users.insert_one(self.user)
        self.load()
        
        return UserActionResponse(True)
    