import requests
from typing import Iterator
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

from nautica.api import Config
from nautica.services.logger import LogManager

from src.lib.Utils import delete_spaces
from src.lib.models.Schedule import WeekSchedule, DaySchedule, Lesson

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

class NSUNetUtil:
    def __init__(self):
        #get the week of the year
        self.calendar = datetime.today().isocalendar()
        self.week = self.calendar.week
        
        if self.calendar.weekday == 7: self.week += 1 #switch to next week on sunday
    
    def failedRequest(self, r: requests.Request, source: str):
        logger.warn(f"Request in {source} failed: {r.url=}, {r.status_code=}")
        logger.warn(f"Response: {r.text}")
        logger.dir(r)
          
    def constructWeekSchedule(self, data: dict, target_week: int, className: str, scheduleType: str):
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
            
            #                                        v--- i'd rather it just fail than overwrite some bs
            days[weekDay].lessons[LESSONS_INDEXED[begin]] = Lesson(
                subject = lesson.get("lesson", {}).get("name", "N/A"),
                teacher = teacher_data.get("name", "N/A"),
                classroom = classroom_data.get("name", "N/A")
            )

        #build mon-sat list (weekdays 1–6), filling missing days with empty schedules
        daysSorted = [
            days.get(i, DaySchedule(date=day_date(i), lessons=[]))
            for i in range(1, 7)
        ]
        
        return WeekSchedule(
            className = className.replace("В", "", 1),
            days = daysSorted,
            firstDay = monday,
            _type = scheduleType
        )
            
    def _fetchSchedule(self, className: str, target_week: int) -> WeekSchedule:
        r = requests.get(f"https://table-ci.nsu.ru/api/schedule/find?group={className}&teacher=&classroom=&week={target_week}&year={self.calendar.year}")
        if not r.ok:
            self.failedRequest(r, "getClassScheduleData")
        return self.constructWeekSchedule(r.json(), target_week, className, "CLASS")

    def getClasses(self): #im so glad they actually made an api 🙏
        r = requests.get("https://table-ci.nsu.ru/api/school-class")
        if not r.ok:
            self.failedRequest(r, "getClasses")
            
        data = r.json()
        for classData in data.get("payload", {}).get("groups", []):
            yield classData.get("name")

    def getClassScheduleData(self, week: int = None) -> Iterator[WeekSchedule]:
        target_week = week or self.week
        classes = list(self.getClasses())

        with ThreadPoolExecutor(max_workers=Config("vki")["schedules.maxConcurrentRequests"]) as executor:
            futures = {executor.submit(self._fetchSchedule, className, target_week) for className in classes}
            for future in as_completed(futures):
                yield future.result()

        
        
        
#example response:
# {
# 	"payload": {
# 		"schedule": {
# 			"2-09:00": [
# 				{
# 					"id": 63255,
# 					"weekday": 2,
# 					"time": {
# 						"id": 89,
# 						"begin": "09:00",
# 						"end": "10:35"
# 					},
# 					"lesson": {
# 						"id": 13376,
# 						"name": "Основы электротехники и электронной техники",
# 						"type": 1
# 					},
# 					"classroom": null,
# 					"teacher": {
# 						"id": 8203,
# 						"name": "Черняйкин И.С."
# 					},
# 					"schoolClasses": [
# 						{
# 							"id": 9009,
# 							"name": "В2408а1",
# 							"parallel": 0,
# 							"subgroup": null
# 						},
# 						{
# 							"id": 9147,
# 							"name": "В2408а2",
# 							"parallel": 0,
# 							"subgroup": null
# 						},
# 						{
# 							"id": 7101,
# 							"name": "В2401а1",
# 							"parallel": 0,
# 							"subgroup": null
# 						},
# 						{
# 							"id": 7200,
# 							"name": "В2401а2",
# 							"parallel": 0,
# 							"subgroup": null
# 						},
# 						{
# 							"id": 7201,
# 							"name": "В2401б1",
# 							"parallel": 0,
# 							"subgroup": null
# 						},
# 						{
# 							"id": 7367,
# 							"name": "В2401б2",
# 							"parallel": 0,
# 							"subgroup": null
# 						}
# 					],
# 					"parity": null,
# 					"show_for_current_week": true,
# 					"parity_label": null,
# 					"parity_type": null
# 				}
# 			],
# 			"2-10:45": [
# 				{
# 					"id": 63256,
# 					"weekday": 2,
# 					"time": {
# 						"id": 90,
# 						"begin": "10:45",
# 						"end": "12:20"
# 					},
# 					"lesson": {
# 						"id": 4552,
# 						"name": "Основы алгоритмизации и программирования",
# 						"type": 1
# 					},
# 					"classroom": {
# 						"id": 103,
# 						"name": "207 КПА"
# 					},
# 					"teacher": {
# 						"id": 10437,
# 						"name": "Голкова Н.В."
# 					},
# 					"schoolClasses": [
# 						{
# 							"id": 7479,
# 							"name": "В2407а1",
# 							"parallel": 0,
# 							"subgroup": null
# 						},
# 						{
# 							"id": 7590,
# 							"name": "В2407а2",
# 							"parallel": 0,
# 							"subgroup": null
# 						},
# 						{
# 							"id": 7591,
# 							"name": "В2407б1",
# 							"parallel": 0,
# 							"subgroup": null
# 						},
# 						{
# 							"id": 7801,
# 							"name": "В2407б2",
# 							"parallel": 0,
# 							"subgroup": null
# 						},
# 						{
# 							"id": 7944,
# 							"name": "В2407в1",
# 							"parallel": 0,
# 							"subgroup": null
# 						},
# 						{
# 							"id": 7945,
# 							"name": "В2407в2",
# 							"parallel": 0,
# 							"subgroup": null
# 						},
# 						{
# 							"id": 8142,
# 							"name": "В2407г1",
# 							"parallel": 0,
# 							"subgroup": null
# 						},
# 						{
# 							"id": 8143,
# 							"name": "В2407г2",
# 							"parallel": 0,
# 							"subgroup": null
# 						},
# 						{
# 							"id": 8304,
# 							"name": "В2407е1",
# 							"parallel": 0,
# 							"subgroup": null
# 						},
# 						{
# 							"id": 8305,
# 							"name": "В2407е2",
# 							"parallel": 0,
# 							"subgroup": null
# 						},
# 						{
# 							"id": 4750,
# 							"name": "В2407з1",
# 							"parallel": 0,
# 							"subgroup": null
# 						},
# 						{
# 							"id": 4835,
# 							"name": "В2407з2",
# 							"parallel": 0,
# 							"subgroup": null
# 						},
# 						{
# 							"id": 5039,
# 							"name": "В2407и1",
# 							"parallel": 0,
# 							"subgroup": null
# 						},
# 						{
# 							"id": 5128,
# 							"name": "В2407и2",
# 							"parallel": 0,
# 							"subgroup": null
# 						},
# 						{
# 							"id": 9009,
# 							"name": "В2408а1",
# 							"parallel": 0,
# 							"subgroup": null
# 						},
# 						{
# 							"id": 9147,
# 							"name": "В2408а2",
# 							"parallel": 0,
# 							"subgroup": null
# 						},
# 						{
# 							"id": 7101,
# 							"name": "В2401а1",
# 							"parallel": 0,
# 							"subgroup": null
# 						},
# 						{
# 							"id": 7200,
# 							"name": "В2401а2",
# 							"parallel": 0,
# 							"subgroup": null
# 						},
# 						{
# 							"id": 7201,
# 							"name": "В2401б1",
# 							"parallel": 0,
# 							"subgroup": null
# 						},
# 						{
# 							"id": 7367,
# 							"name": "В2401б2",
# 							"parallel": 0,
# 							"subgroup": null
# 						}
# 					],
# 					"parity": null,
# 					"show_for_current_week": true,
# 					"parity_label": null,
# 					"parity_type": null
# 				}
# 			],
# 			"3-09:00": [
# 				{
# 					"id": 63268,
# 					"weekday": 3,
# 					"time": {
# 						"id": 89,
# 						"begin": "09:00",
# 						"end": "10:35"
# 					},
# 					"lesson": {
# 						"id": 6388,
# 						"name": "Физика",
# 						"type": 3
# 					},
# 					"classroom": {
# 						"id": 73,
# 						"name": "412"
# 					},
# 					"teacher": {
# 						"id": 8204,
# 						"name": "Ильина О.А."
# 					},
# 					"schoolClasses": [
# 						{
# 							"id": 7101,
# 							"name": "В2401а1",
# 							"parallel": 0,
# 							"subgroup": null
# 						},
# 						{
# 							"id": 7200,
# 							"name": "В2401а2",
# 							"parallel": 0,
# 							"subgroup": null
# 						}
# 					],
# 					"parity": null,
# 					"show_for_current_week": true,
# 					"parity_label": null,
# 					"parity_type": null
# 				}
# 			],
# 			"3-10:45": [
# 				{
# 					"id": 63283,
# 					"weekday": 3,
# 					"time": {
# 						"id": 90,
# 						"begin": "10:45",
# 						"end": "12:20"
# 					},
# 					"lesson": {
# 						"id": 13336,
# 						"name": "Учебная практика ПМ.03 Техническое обслуживание и ремонт компьютерных систем и комплексов",
# 						"type": 3
# 					},
# 					"classroom": {
# 						"id": 81,
# 						"name": "301"
# 					},
# 					"teacher": {
# 						"id": 15091,
# 						"name": "Краснов Л.П."
# 					},
# 					"schoolClasses": [
# 						{
# 							"id": 7101,
# 							"name": "В2401а1",
# 							"parallel": 0,
# 							"subgroup": null
# 						}
# 					],
# 					"parity": null,
# 					"show_for_current_week": true,
# 					"parity_label": null,
# 					"parity_type": null
# 				}
# 			],
# 			"3-13:00": [
# 				{
# 					"id": 63286,
# 					"weekday": 3,
# 					"time": {
# 						"id": 91,
# 						"begin": "13:00",
# 						"end": "14:35"
# 					},
# 					"lesson": {
# 						"id": 6384,
# 						"name": "Математика",
# 						"type": 2
# 					},
# 					"classroom": {
# 						"id": 92,
# 						"name": "102"
# 					},
# 					"teacher": {
# 						"id": 26444,
# 						"name": "Табиханова З.Е."
# 					},
# 					"schoolClasses": [
# 						{
# 							"id": 7101,
# 							"name": "В2401а1",
# 							"parallel": 0,
# 							"subgroup": null
# 						},
# 						{
# 							"id": 7200,
# 							"name": "В2401а2",
# 							"parallel": 0,
# 							"subgroup": null
# 						}
# 					],
# 					"parity": null,
# 					"show_for_current_week": true,
# 					"parity_label": null,
# 					"parity_type": null
# 				}
# 			],
# 			"4-10:45": [
# 				{
# 					"id": 63410,
# 					"weekday": 4,
# 					"time": {
# 						"id": 90,
# 						"begin": "10:45",
# 						"end": "12:20"
# 					},
# 					"lesson": {
# 						"id": 13386,
# 						"name": "Техническое обслуживание и ремонт аппаратной части компьютерных систем и комплексов",
# 						"type": 3
# 					},
# 					"classroom": {
# 						"id": 81,
# 						"name": "301"
# 					},
# 					"teacher": {
# 						"id": 8522,
# 						"name": "Кутузов М.А."
# 					},
# 					"schoolClasses": [
# 						{
# 							"id": 7101,
# 							"name": "В2401а1",
# 							"parallel": 0,
# 							"subgroup": null
# 						}
# 					],
# 					"parity": null,
# 					"show_for_current_week": true,
# 					"parity_label": null,
# 					"parity_type": null
# 				}
# 			],
# 			"4-13:00": [
# 				{
# 					"id": 63434,
# 					"weekday": 4,
# 					"time": {
# 						"id": 91,
# 						"begin": "13:00",
# 						"end": "14:35"
# 					},
# 					"lesson": {
# 						"id": 13386,
# 						"name": "Техническое обслуживание и ремонт аппаратной части компьютерных систем и комплексов",
# 						"type": 1
# 					},
# 					"classroom": {
# 						"id": 58,
# 						"name": "414"
# 					},
# 					"teacher": {
# 						"id": 8522,
# 						"name": "Кутузов М.А."
# 					},
# 					"schoolClasses": [
# 						{
# 							"id": 7101,
# 							"name": "В2401а1",
# 							"parallel": 0,
# 							"subgroup": null
# 						},
# 						{
# 							"id": 7200,
# 							"name": "В2401а2",
# 							"parallel": 0,
# 							"subgroup": null
# 						},
# 						{
# 							"id": 7201,
# 							"name": "В2401б1",
# 							"parallel": 0,
# 							"subgroup": null
# 						},
# 						{
# 							"id": 7367,
# 							"name": "В2401б2",
# 							"parallel": 0,
# 							"subgroup": null
# 						}
# 					],
# 					"parity": null,
# 					"show_for_current_week": true,
# 					"parity_label": null,
# 					"parity_type": null
# 				}
# 			],
# 			"4-14:45": [
# 				{
# 					"id": 63445,
# 					"weekday": 4,
# 					"time": {
# 						"id": 92,
# 						"begin": "14:45",
# 						"end": "16:20"
# 					},
# 					"lesson": {
# 						"id": 4552,
# 						"name": "Основы алгоритмизации и программирования",
# 						"type": 3
# 					},
# 					"classroom": {
# 						"id": 56,
# 						"name": "302"
# 					},
# 					"teacher": {
# 						"id": 3964,
# 						"name": "Белякова М.А."
# 					},
# 					"schoolClasses": [
# 						{
# 							"id": 7101,
# 							"name": "В2401а1",
# 							"parallel": 0,
# 							"subgroup": null
# 						}
# 					],
# 					"parity": null,
# 					"show_for_current_week": true,
# 					"parity_label": null,
# 					"parity_type": null
# 				}
# 			],
# 			"5-09:00": [
# 				{
# 					"id": 63459,
# 					"weekday": 5,
# 					"time": {
# 						"id": 89,
# 						"begin": "09:00",
# 						"end": "10:35"
# 					},
# 					"lesson": {
# 						"id": 11701,
# 						"name": "Физическая культура",
# 						"type": 2
# 					},
# 					"classroom": null,
# 					"teacher": {
# 						"id": 33773,
# 						"name": "Балашов М.А."
# 					},
# 					"schoolClasses": [
# 						{
# 							"id": 7101,
# 							"name": "В2401а1",
# 							"parallel": 0,
# 							"subgroup": null
# 						},
# 						{
# 							"id": 7200,
# 							"name": "В2401а2",
# 							"parallel": 0,
# 							"subgroup": null
# 						}
# 					],
# 					"parity": null,
# 					"show_for_current_week": true,
# 					"parity_label": null,
# 					"parity_type": null
# 				}
# 			],
# 			"5-10:45": [
# 				{
# 					"id": 63466,
# 					"weekday": 5,
# 					"time": {
# 						"id": 90,
# 						"begin": "10:45",
# 						"end": "12:20"
# 					},
# 					"lesson": {
# 						"id": 6387,
# 						"name": "Русский язык",
# 						"type": 2
# 					},
# 					"classroom": {
# 						"id": 55,
# 						"name": "233"
# 					},
# 					"teacher": {
# 						"id": 8595,
# 						"name": "Клюшова Е.В."
# 					},
# 					"schoolClasses": [
# 						{
# 							"id": 7101,
# 							"name": "В2401а1",
# 							"parallel": 0,
# 							"subgroup": null
# 						},
# 						{
# 							"id": 7200,
# 							"name": "В2401а2",
# 							"parallel": 0,
# 							"subgroup": null
# 						}
# 					],
# 					"parity": null,
# 					"show_for_current_week": true,
# 					"parity_label": null,
# 					"parity_type": null
# 				}
# 			],
# 			"5-13:00": [
# 				{
# 					"id": 63487,
# 					"weekday": 5,
# 					"time": {
# 						"id": 91,
# 						"begin": "13:00",
# 						"end": "14:35"
# 					},
# 					"lesson": {
# 						"id": 6388,
# 						"name": "Физика",
# 						"type": 1
# 					},
# 					"classroom": {
# 						"id": 98,
# 						"name": "Читальный зал А"
# 					},
# 					"teacher": {
# 						"id": 4844,
# 						"name": "Аксенов М.С."
# 					},
# 					"schoolClasses": [
# 						{
# 							"id": 7101,
# 							"name": "В2401а1",
# 							"parallel": 0,
# 							"subgroup": null
# 						},
# 						{
# 							"id": 7200,
# 							"name": "В2401а2",
# 							"parallel": 0,
# 							"subgroup": null
# 						},
# 						{
# 							"id": 7201,
# 							"name": "В2401б1",
# 							"parallel": 0,
# 							"subgroup": null
# 						},
# 						{
# 							"id": 7367,
# 							"name": "В2401б2",
# 							"parallel": 0,
# 							"subgroup": null
# 						}
# 					],
# 					"parity": null,
# 					"show_for_current_week": true,
# 					"parity_label": null,
# 					"parity_type": null
# 				}
# 			],
# 			"6-09:00": [
# 				{
# 					"id": 63508,
# 					"weekday": 6,
# 					"time": {
# 						"id": 89,
# 						"begin": "09:00",
# 						"end": "10:35"
# 					},
# 					"lesson": {
# 						"id": 6384,
# 						"name": "Математика",
# 						"type": 2
# 					},
# 					"classroom": {
# 						"id": 92,
# 						"name": "102"
# 					},
# 					"teacher": {
# 						"id": 26444,
# 						"name": "Табиханова З.Е."
# 					},
# 					"schoolClasses": [
# 						{
# 							"id": 7101,
# 							"name": "В2401а1",
# 							"parallel": 0,
# 							"subgroup": null
# 						},
# 						{
# 							"id": 7200,
# 							"name": "В2401а2",
# 							"parallel": 0,
# 							"subgroup": null
# 						}
# 					],
# 					"parity": null,
# 					"show_for_current_week": true,
# 					"parity_label": null,
# 					"parity_type": null
# 				}
# 			],
# 			"6-10:45": [
# 				{
# 					"id": 63550,
# 					"weekday": 6,
# 					"time": {
# 						"id": 90,
# 						"begin": "10:45",
# 						"end": "12:20"
# 					},
# 					"lesson": {
# 						"id": 4539,
# 						"name": "Иностранный язык в профессиональной деятельности",
# 						"type": 2
# 					},
# 					"classroom": {
# 						"id": 66,
# 						"name": "229"
# 					},
# 					"teacher": {
# 						"id": 10641,
# 						"name": "Бессонова В.А."
# 					},
# 					"schoolClasses": [
# 						{
# 							"id": 7101,
# 							"name": "В2401а1",
# 							"parallel": 0,
# 							"subgroup": null
# 						},
# 						{
# 							"id": 7200,
# 							"name": "В2401а2",
# 							"parallel": 0,
# 							"subgroup": null
# 						}
# 					],
# 					"parity": null,
# 					"show_for_current_week": true,
# 					"parity_label": null,
# 					"parity_type": null
# 				}
# 			]
# 		}
# 	}
# }