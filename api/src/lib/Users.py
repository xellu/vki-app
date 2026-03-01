from cryptography.fernet import Fernet

from .models.User import UserModel, SanitizeUser

from nautica.api import MongoDB, Config
from nautica.services.logger import LogManager
from nautica.services.shell.descriptor import ShellCommand

# from plugins.intercom import Intercom

logger = LogManager("Lib.Users")
fernet = Fernet(Config("auth")["encryptionKey"])

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
            raise ValueError("User ID or NSU E-mail must be provided")
        
        self.load()
        
    def is_valid(self) -> bool:
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
    
    def update(self) -> UserActionResponse:
        """Update the user in the database."""
        if not self.is_valid():
            return UserActionResponse(False, "User not found")
        
        MongoDB("vki").users.update_one({"_id": self.uid}, {"$set": self.user})        
        
        return UserActionResponse(True)
    
    def get(self, key: str = None, fallback = None) -> dict | None:
        if not key:            
            return self.user
        return self.user.get(key, fallback)

    def get_profile(self):
        return SanitizeUser(self.user.copy())

    def delete(self) -> UserActionResponse:
        """Delete the user."""
        if not self.is_valid():
            return UserActionResponse(False, "User not found")
        
        #TODO: remove all roles
        
        MongoDB("vki").users.delete_one({"_id": self.uid})
        self.user = None
        
        return UserActionResponse(True)
    
    def encrypt_password(self, password) -> str:
        return fernet.encrypt(password.encode()).decode()
    
    def decrypt_password(self) -> str | None:
        if not self.is_valid(): return
        
        try:
            return fernet.decrypt(self.get("password").encode()).decode()
        except Exception as err:
            logger.trace(err)
    
    def create(self, email = None, password = None) -> UserActionResponse:
        """Create a new user."""
        if self.is_valid():
            return UserActionResponse(False, "User already exists")
        
        self.user = UserModel()
        if not email and not password:
            return UserActionResponse(False, "Email or password is missing")
        
        self.user["email"] = email
        self.user["password"] = self.encrypt_password(password)
        
        MongoDB("vki").users.insert_one(self.user)
        self.load()
        
        return UserActionResponse(True)
    
@ShellCommand("users.keygen", "Generate an encryption key for users", "users.keygen")
def users_keygen(*args, **kwargs):
    key = Fernet.generate_key()
    logger.ok(f"Generated key: {key.decode()}")
    logger.ok("Save this key to 'auth.config.json', make sure it does not leak :3")