from dataclasses import dataclass, field
from uuid import uuid4
import datetime

@dataclass
class Lesson:
    index: int #when it's taking place, see below:    
    # 1п:  9:00-9:45  |  9:50-10:35
    # 2п: 10:45-11:30 | 11:35-12:20
    #     lunch break - 40min
    # 3п: 13:00-13:45 | 13:50-14:35
    # 4п: 14:45-15:30 | 15:35-16:20
    # 5п: 16:30-17:15 | 17:20-18:05
    
    subject: str #e.g. "Matematika"
    teacher: str #pretty self explanatory
    classroom: str #where the lesson is taking place (e.g. "101")
    
    changes: dict = field(default_factory=dict)
    #"attribute": ["previous value", "new value"], for example:
    # {     the old one --v
    #     "classroom": ["101", "414"]    
    # }                          ^-- the new one
    
    isCancelled: bool = False

    
@dataclass
class DaySchedule:
    date: str #the date that got regex'd from the pdf
    dateParsed: datetime.datetime  #a timestamp i got after some more buffoonery with the date
    
    lessons: list[Lesson]
    
@dataclass
class WeekSchedule:
    _id = f"wsh_{uuid4().hex}"
    
    className: str #e.g. 2401a1
    days: list[DaySchedule]