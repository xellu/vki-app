from enum import Enum

class Messages(Enum):
    SCHEDULE_DOWNLOAD_ERROR = "scheduleDownloadError"
    SCHEDULE_PARSING_ERROR = "scheduleParseError"
    SCHEDULE_DIFF_GEN_ERROR = "scheduleDiffError"