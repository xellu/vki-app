from nautica.api.http import (
    Context, 
    Request,
    Require,
    
    Reply,
    ReplyList,
    Error,
)

from src.lib.schedule.Networking import download_timetables
from src.lib.schedule.Parser import parse_schedule_from_pdf

from nautica.ext.utils import walkPath
from nautica.api import Config
import os

@Request.GET()
async def timetables(ctx: Context):
    if not os.path.exists(Config("vki")["schedules.pdfTemp"]):
        download_timetables()
        
    out = []
    for file in walkPath(Config("vki")["schedules.pdfTemp"]):
        if not file.endswith(".pdf"): continue
        
        out.append(parse_schedule_from_pdf(file))
        