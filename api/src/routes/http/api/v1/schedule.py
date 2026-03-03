from nautica.api.http import (
    Context, 
    Request,
    Require,
    
    Reply,
    ReplyList,
    Error,
)

from src.lib.schedule.Runner import Schedules, ScheduleDB
from nautica.services.logger import LogManager

logger = LogManager("Routes.Http.Schedule")

@Request.GET()
async def timetables(ctx: Context):
    classIds = ScheduleDB.data_keyed.copy()
    out = {}
    for className, classId in classIds.items():
        if not className: continue #skip unknown class names
        
        out[className] = ScheduleDB.getById(classId)
        
    return Reply(
        schedule=out,
        next_update=Schedules.next_update,
        error = Schedules.error
    )