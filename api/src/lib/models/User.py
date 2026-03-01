import uuid
import time

def UserModel():
    return {
        "_id": f"usr_{uuid.uuid4().hex}",
        
        "email": "", #login email used for cab.nsu.ru
        "password": "", #encrypted password from cab.nsu.ru
        
        "name": "", #first and last name pulled from, you guessed it, cab.nsu
        "group": "", #the class a person is from

        #user preferences
        "settings": {
            "timetable": None, #str/null, preferred time table to show.
            #              ^ if None, it'll default to "group" attribute
            
            "langId": "ru_ru", #default app language
        },
                
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