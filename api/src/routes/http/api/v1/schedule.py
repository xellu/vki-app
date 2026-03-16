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

@Request.GET("class")
async def class_timetable(ctx: Context):
    
    if ctx.query.get("id"):
        tt = ScheduleDB.getById(ctx.query.get("id"))
        if not tt or tt.get("_type") != "CLASS": return Error("Class not found"), 404
    
        return Reply( schedule = tt, next_update=Schedules.next_update, error = Schedules.error )
    
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

@Request.GET("list/class")
async def list_teachers(ctx):
    classIds = ScheduleDB.data_keyed.copy()
    out = []
    for className, classId in classIds.items():
        if not className: continue #skip unknown class names
        
        data = ScheduleDB.getById(classId)
        if data.get("_type") == "CLASS":
            out.append(className)
    return Reply(list=out) #ReplyList is broken in nautica lol
    

#-----------------------
    
@Request.GET("teacher") #TODO: fix, returns 404 - same w classrooms
@Require.query(id=str)
async def teacher_timetable(ctx: Context):
    tt = ScheduleDB.getById(ctx.query.get("id"))
    if not tt or tt.get("_type") != "TEACHER": return Error("Teacher not found"), 404

    return Reply( schedule = tt, next_update=Schedules.next_update, error = Schedules.error )

@Request.GET("list/teacher")
async def list_teachers(ctx):
    classIds = ScheduleDB.data_keyed.copy()
    out = []
    for className, classId in classIds.items():
        if not className: continue #skip unknown class names
        
        data = ScheduleDB.getById(classId)
        if data.get("_type") == "TEACHER":
            out.append(className)
    return Reply(list=out)
    
#------------------------------

@Request.GET("classroom")
@Require.query(id=str)
async def classroom_timetable(ctx: Context):
    tt = ScheduleDB.getById(ctx.query.get("id"))
    if not tt or tt.get("_type") != "CLASSROOM": return Error("Classroom not found"), 404

    return Reply( schedule = tt, next_update=Schedules.next_update, error = Schedules.error )


@Request.GET("list/classroom")
async def list_classroom(ctx):
    classIds = ScheduleDB.data_keyed.copy()
    out = []
    for className, classId in classIds.items():
        if not className: continue #skip unknown class names
        
        data = ScheduleDB.getById(classId)
        if data.get("_type") == "CLASSROOM":
            out.append(className)
    return Reply(list=out)
    