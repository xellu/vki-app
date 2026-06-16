import requests
from typing import Iterator
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

from nautica.api import Config
from nautica.services.logger import LogManager

from src.lib.Utils import delete_spaces
from src.lib.models.Schedule import WeekSchedule, DaySchedule, Lesson, SubjectType

logger = LogManager("Lib.Schedule.Networking")

LESSONS_INDEXED = {
    #begin time: index
    "9:00": 0,
    "09:00": 0,
    "10:45": 1,
    "13:00": 2,
    "14:45": 3,
    "16:30": 4,
    "18:15": 5
}

class NSUTablesUtil:
    def __init__(self):
        #get the week of the year
        self.calendar = datetime.today().isocalendar()
        self.week = self.calendar.week
        
        if self.calendar.weekday == 7: self.week += 1 #switch to next week on sunday
    
    def failedRequest(self, r: requests.Request, source: str) -> None:
        logger.warn(f"Request in {source} failed: {r.url=}, {r.status_code=}")
        logger.warn(f"Response: {r.text}")
        logger.dir(r)
        
    #a bit of parsing---------------------  
    def constructWeekSchedule(self, data: dict, target_week: int, className: str, scheduleType: str) -> WeekSchedule:
        def day_date(weekday: int) -> datetime:
            return monday + timedelta(days=weekday - 1)
        
        #get first day of the week
        monday = datetime.fromisocalendar(self.calendar.year, target_week, 1)
        days: dict[int, DaySchedule] = {}

        #api returns a dict keyed by "weekday-time" (e.g. "2-09:00")????
        #they r a list of lesson objects
        _schedule = data.get("payload", {}).get("schedule", {})

        if isinstance(_schedule, dict):
            all_lessons = [lesson for slot in _schedule.values() if isinstance(slot, list) for lesson in slot]
        else:
            all_lessons = _schedule  # fallback for list format

        for lesson in all_lessons:
            #skip bullshit data (hopefully)
            if not isinstance(lesson, dict):
                logger.warn(f"'{lesson}' is not dict, skipping")
                continue

            weekDay = lesson.get("weekday")
            if weekDay is None:
                continue

            if weekDay not in days: #create a new day and fill it with lessons
                dayLessons = [Lesson(subject="N/A", teacher="N/A", classroom="N/A") for _ in range(6)] #there should be only 5 classes per day max - apparently not
                days[weekDay] = DaySchedule(date=day_date(weekDay), lessons=dayLessons)
            
            teacher_data = lesson.get("teacher") or {}
            classroom_data = lesson.get("classroom") or {}
            
            begin = lesson.get("time", {}).get("begin")
            
            #get lesson type
            _type = SubjectType.SEMINAR
            match str(lesson.get("lesson", {}).get("type")):
                case "3": _type = SubjectType.LAB
                case "2": _type = SubjectType.PRACTICAL
                case "1": _type = SubjectType.LESSON
            
            parallelGroups = []
            for group in lesson.get("schoolClasses", []):
                parallelGroups.append(group.get("name").replace('В', '', 1))
            
            #                                        v--- i'd rather it just fail than overwrite some bs
            days[weekDay].lessons[LESSONS_INDEXED[begin]] = Lesson(
                subject = lesson.get("lesson", {}).get("name", "N/A"),
                teacher = teacher_data.get("name", "N/A"),
                classroom = classroom_data.get("name", "N/A"),
                
                parallelGroups = parallelGroups,
                _type = _type
            )

        #build mon-sat list (weekdays 1–6), filling missing days with empty schedules
        daysSorted = [
            days.get(i, DaySchedule(date=day_date(i), lessons=[]))
            for i in range(1, 7)
        ]
        
        return WeekSchedule(
            className = className.replace("В", "", 1) if scheduleType == "CLASS" else className, #remove the fuckass letter at the start of the group name (B2407a1 -> 2407a1)
            days = daysSorted,
            firstDay = monday,
            _type = scheduleType
        )
    
    def _fetchSchedule(self, target_week: int, className: str = "", teacher: str = "", classroom: str = "") -> WeekSchedule:
        r = requests.get(f"https://table-ci.nsu.ru/api/schedule/find?group={className}&teacher={teacher}&classroom={classroom}&week={target_week}&year={self.calendar.year}")
        if not r.ok:
            self.failedRequest(r, "getClassScheduleData")
        
        scheduleName = className or teacher or classroom
        scheduleType = "CLASS" if className else ("TEACHER" if teacher else "CLASSROOM")
        # print(scheduleType)
        return self.constructWeekSchedule(r.json(), target_week, scheduleName, scheduleType)
    
    #timetables------------
    def getAllSchedules(self, week: int = None) -> Iterator[WeekSchedule]:
        for s in self.getClassScheduleData(week):
            yield s
        for s in self.getTeacherScheduleData(week):
            yield s
        for s in self.getClassroomScheduleData(week):
            yield s
        
        
    
    #timetables for classes----------------------     
    def getClasses(self) -> list[str]: #im so glad they actually made an api 🙏
        r = requests.get("https://table-ci.nsu.ru/api/school-class")
        if not r.ok:
            self.failedRequest(r, "getClasses")
            
        data = r.json()
        _classes = []
        for classData in data.get("payload", {}).get("groups", []):
            _classes.append(classData.get("name"))
        return _classes #not really a point to use an iterator i guess

    def getClassScheduleData(self, week: int = None) -> Iterator[WeekSchedule]:
        target_week = week or self.week
        classes = self.getClasses()

        with ThreadPoolExecutor(max_workers=Config("vki")["schedules.maxConcurrentRequests"]) as executor:
            futures = {executor.submit(self._fetchSchedule, target_week, className=className) for className in classes}
            for future in as_completed(futures):
                yield future.result()

    def getPerClassScheduleData(self, className: str, week: int = None) -> Iterator[WeekSchedule]:
        return self._fetchSchedule(className, week or self.week)

    #timetables for teachers-----------------------
    #potentionally just construct all the other schedules from the class timetables?
    
    def _getPartialTeacherList(self, filter) -> list[str]:
        r = requests.get(f"https://table-ci.nsu.ru/api/teacher?filter={filter}")
        teachers = []
        if r.ok:
            for teach in r.json().get("payload", {}).get("teachers", []):
                teachers.append(teach.get("name"))
            return teachers
        
        self.failedRequest(r, "_getPartialTeacherList")
        return []

    def getTeachers(self) -> Iterator[str]:
        def getFilters() -> list[str]:
            r = requests.get("https://table-ci.nsu.ru/api/teacher/filters")
            if not r.ok:
                self.failedRequest(r, "getTeachers")
                
            data = r.json()
            filters = []
            for filter in data.get("payload", {}).get("filters", []):
                filters.append(filter.get("text"))
                
            return filters
        
        with ThreadPoolExecutor(max_workers=Config("vki")["schedules.maxConcurrentRequests"]) as executor:
            futures = {executor.submit(self._getPartialTeacherList, filter) for filter in getFilters()}
            for future in as_completed(futures):
                for teach in future.result(): yield teach
                    
    def getTeacherScheduleData(self, week: int = None) -> Iterator[WeekSchedule]:
        target_week = week or self.week
        teachers = list(self.getTeachers())

        with ThreadPoolExecutor(max_workers=Config("vki")["schedules.maxConcurrentRequests"]) as executor:
            futures = {executor.submit(self._fetchSchedule, target_week, teacher=teacher) for teacher in teachers}
            for future in as_completed(futures):
                yield future.result()
                
    #timetables for classrooms---------------
    def _getPartialClassroomList(self, filter) -> list[str]:
        r = requests.get(f"https://table-ci.nsu.ru/api/classroom?filter={filter}")
        classrooms = []
        if r.ok:
            for teach in r.json().get("payload", {}).get("classrooms", []):
                classrooms.append(teach.get("name"))
            return classrooms
        
        self.failedRequest(r, "_getPartialClassroomList")
        return []
        
    def getClassrooms(self) -> Iterator[str]:
        def getFilters() -> list[str]:
            r = requests.get("https://table-ci.nsu.ru/api/classroom/filters")
            if not r.ok:
                self.failedRequest(r, "getTeachers")
                
            data = r.json()
            filters = []
            for filter in data.get("payload", {}).get("filters", []):
                filters.append(filter.get("text"))
                
            return filters #wow i love boilerplate 👍👍👍👍👍
        
        with ThreadPoolExecutor(max_workers=Config("vki")["schedules.maxConcurrentRequests"]) as executor:
            futures = {executor.submit(self._getPartialClassroomList, filter) for filter in getFilters()}
            for future in as_completed(futures):
                for teach in future.result(): yield teach
                
    def getClassroomScheduleData(self, week: int = None) -> Iterator[WeekSchedule]:
        target_week = week or self.week
        classrooms = list(self.getClassrooms())

        with ThreadPoolExecutor(max_workers=Config("vki")["schedules.maxConcurrentRequests"]) as executor:
            futures = {executor.submit(self._fetchSchedule, target_week, classroom=classroom) for classroom in classrooms}
            for future in as_completed(futures):
                yield future.result()