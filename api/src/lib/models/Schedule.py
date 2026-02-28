from dataclasses import dataclass, field
from uuid import uuid4
import datetime

@dataclass
class Lesson:
    # index: int #when it's taking place, see below: not needed, its sorted like it should be already
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

    def to_dict(self) -> dict:
        return {
            "subject": self.subject,
            "teacher": self.teacher,
            "classroom": self.classroom,
            "changes": self.changes,
            "isCancelled": self.isCancelled,
        }


@dataclass
class DaySchedule:
    date: datetime.datetime

    lessons: list[Lesson]

    def to_dict(self) -> dict:
        return {
            "date": self.date.timestamp() if self.date != datetime.datetime.min else None,
            "lessons": [l.to_dict() for l in self.lessons],
        }


@dataclass
class WeekSchedule:
    className: str #e.g. 2401a1
    days: list[DaySchedule]
    firstDay: datetime.datetime = None

    def to_dict(self) -> dict:
        first = self.firstDay or (self.days[0].date if self.days else None)
        return {
            "className": self.className,
            "days": [d.to_dict() for d in self.days],
            "firstDay": first.timestamp() if first else None,
        }
