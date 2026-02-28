import time
from threading import Thread

from nautica.api import Eventer
from nautica.services.logger import LogManager
from nautica.services.database.xeldb import XelDB


from src.lib.schedule.Networking import download_timetables
from src.lib.schedule.Parser import parse_schedule_from_pdf

ScheduleDB = XelDB("schedule", primary_key="className")
logger = LogManager("Lib.Schedule.Runner")

class ScheduleManager:
    def __init__(self, update_period: int = 300):
        self.update_period = update_period
        self.next_update = 0
        
        self.running = False
    
        self.thread = None
    
    def start(self):
        self.thread = Thread(target=self.update_schedule)
        self.thread.start()
        logger.ok("Started schedule manager")
        
    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(30)
        logger.ok("Stopped schedule manager")
    
    def update_schedule(self):
        while self.running:
            if time.time() < self.next_update:
                time.sleep(1/4)
            
            self.next_update = time.time() + self.update_period
            download_timetables()
            schedule = parse_schedule_from_pdf()
            
            self.create_diff(schedule)
            
    def create_diff(self, schedule: dict):
        if not schedule:
            return

        # Determine the new week's firstDay from any entry in the parsed schedule
        sample = next(iter(schedule.values()))
        new_first_day = sample.to_dict()["firstDay"]

        existing = ScheduleDB.filter(lambda _: True)
        is_new_week = not existing or existing[0].get("firstDay") != new_first_day

        if is_new_week:
            logger.info(f"New week detected (firstDay={new_first_day}), rebuilding schedule DB")
            for item in existing:
                ScheduleDB.removeByKey(item["className"])
            for week in schedule.values():
                ScheduleDB.create(**week.to_dict())
            return

        # Same week — compute diffs relative to the original (start-of-week) state
        for class_name, week in schedule.items():
            stored = ScheduleDB.getByKey(class_name)

            if stored is None:
                ScheduleDB.create(**week.to_dict())
                continue

            stored_days = stored.get("days", [])
            for d_idx, new_day in enumerate(week.days):
                if d_idx >= len(stored_days):
                    break
                stored_lessons = stored_days[d_idx].get("lessons", [])

                for l_idx, new_lesson in enumerate(new_day.lessons):
                    if l_idx >= len(stored_lessons):
                        break
                    stored_lesson = stored_lessons[l_idx]
                    stored_changes = stored_lesson.get("changes", {})

                    changes = {}
                    for attr in ("subject", "teacher", "classroom", "isCancelled"):
                        new_val = getattr(new_lesson, attr)
                        # Baseline is the original value from the start of the week,
                        # not the most recently stored value (to preserve change history correctly)
                        baseline = stored_changes[attr][0] if attr in stored_changes else stored_lesson.get(attr)
                        if new_val != baseline:
                            changes[attr] = [baseline, new_val]

                    new_lesson.changes = changes

            ScheduleDB.setByKey(class_name, "days", [d.to_dict() for d in week.days])
            
Schedules = ScheduleManager()

@Eventer.on("shutdown")
def on_shutdown(reason: str = None):
    Schedules.stop()