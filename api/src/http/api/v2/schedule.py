from napi.http import (
    HTTP,
    Context,
    Reply,
    Error
)

from nautica import Services

from src.nauth import Auth
from plugins.ScheduleRunner import ScheduleRunner

@HTTP.GET("/all")
# @Auth.Protect()
async def all_timetables():
    Schedules: ScheduleRunner = Services.get("ScheduleRunner")
    ScheduleDB = Schedules.ScheduleDB
    
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
    
@HTTP.GET("/list")
async def list_timetables():
    ScheduleDB: ScheduleRunner = Services.get("ScheduleRunner").ScheduleDB

    classIds = ScheduleDB.data_keyed.copy()
    
    out = {}
    for className, classId in classIds.items():
        if not className: continue #skip unknown class names
        
        s = ScheduleDB.getById(classId)
        if not s: continue
        
        _type = str(s.get("_type")).lower() #create categories
        if _type not in out: out[_type] = []
        
        out[_type].append(className) #sort into categories
        
    return Reply(**out)

@HTTP.GET("for")
@HTTP.Require(query={"id": str})
async def timetables_for(ctx: Context):
    ScheduleDB: ScheduleRunner = Services.get("ScheduleRunner").ScheduleDB
    tt = ScheduleDB.getByKey(ctx.query.get("id"))
    if not tt:
        return Error(404, "Timetable not found")
    
    return Reply(**tt)