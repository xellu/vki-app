import uuid
import time

def UserModel():
    return {
        "_id": f"usr_{uuid.uuid4().hex}",
        
        "email": "", #login email used for cab.nsu.ru
        "password": "", #AES encrypted password from cab.nsu.ru
        
        "name": "", #first and last name pulled from, you guessed it, cab.nsu
        "timetable": "", #configured schedule timetable
        
        "cabNsuCookie": "",
        
        "inbox": [ #notifications
            # {
            #     "title": "Notification Label",
            #     "body": "markdown content here!",
            #     "createdAt": time.time()
            #     "read": False,
            # }
        ],
        
        
        "createdAt": time.time()
    }    
    
def SanitizeUser(user: dict):
    """
    Removes all keys from a user object that are not in the UserTemplate and sensitive information
    """
    
    BLACKLIST = [
        "password",
        "cabNsuCookie"
    ]
    
    if not type(user) == dict:
        return None
    
    user = user.copy()
    
    for key in user.copy():
        if key not in UserModel():
            del user[key]
            
        if key in BLACKLIST:
            del user[key]
            
    return user