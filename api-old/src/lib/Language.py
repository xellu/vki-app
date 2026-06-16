from enum import Enum

class Messages(Enum):
    SCHEDULE_DOWNLOAD_ERROR = "scheduleDownloadError"
    SCHEDULE_PARSING_ERROR = "scheduleParseError"
    SCHEDULE_DIFF_GEN_ERROR = "scheduleDiffError"
    
    AUTH_CANT_GET_SESSION = "cantGetSession"
    AUTH_EXPIRED_SESSION = "expiredSession"
    
    NSUAPI_INVALID_LOGIN = "invalidLogin"