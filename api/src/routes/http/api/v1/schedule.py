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

@Request.GET("all")
async def all_timetables(ctx: Context):
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

@Request.GET("list")
async def list_timetables(ctx):
    classIds = ScheduleDB.data_keyed.copy()
    
    out = {}
    for className, classId in classIds.items():
        if not className: continue #skip unknown class names
        
        s = ScheduleDB.getById(classId)
        if not s: continue
        
        _type = str(s.get("_type")).lower() #create categories
        if _type not in out: out[_type] = []
        
        out[_type].append(className) #sort into categories
        
    return Reply(**out) #ReplyList is broken in nautica lol
    

@Request.GET("for")
@Require.query(id=str)
async def timetable_for(ctx: Context):
    tt = ScheduleDB.getByKey(ctx.query.get("id"))
    if not tt:
        return Error("Timetable not found"), 404
    
    return Reply(**tt)