import time
import json
from threading import Thread

from napi import Require
from nautica import Service, Config, Logger as logger, Services
from nautica.services.builtins.shell.decorator import RegisterCommand, CommandRequirements

from src.lib.Language import Messages

from plugins.ScheduleNetworking import NSUTablesUtil
from plugins.XelDB import XelDB

class ScheduleRunner(Service):
    def __init__(self):
        super().__init__()
        
        self.update_period = 600
        self.next_update = 0
        self.last_update = time.time()
        
        self.running = False
    
        self.thread = None
        self.error = None
    
        self.ScheduleDB: XelDB.Instance = None
    
    def onSetup(self, registry):
        self.ScheduleDB = registry["XelDB"].create("Cache-Schedule", primary_key="className")
    
        self.next_update = Config("vki")["schedules.updateInterval"]
        self.last_update = Config("vki").get("persist.scheduleNextUpdate", 0)
            
        @RegisterCommand("schedule.update", "Updates the schedule from remote")
        def reset_schedule_cooldown(*args, **kwargs):
            if not self.running:
                self.onStart(Services)
                
            self.next_update = 0
            
        @RegisterCommand("test", "test")
        def test_command(*args, **kwargs):
            for teach in NSUTablesUtil().getClassroomScheduleData():
                print(teach)
            
        @RegisterCommand("schedule.dump", "Dumps lesson data from all schedules into a file",
            CommandRequirements(
                args = {"field": Require.AnyOf("subject", "teacher", "classroom", "raw", "*")},
                flags = ["noduplicates"]
            )
        )
        def dump_schedule_data(field, noduplicates: bool = False):
            out = []
            if field in ["subject", "teacher", "classroom", "*"]:
                for _, classId in self.ScheduleDB.data_keyed.items():
                    week = self.ScheduleDB.getById(classId)
                    for day in week.get("days", []):
                        for lesson in day.get("lessons", []):
                            #handle full lesson dump
                            if field == "*":
                                out.append(lesson)
                                continue
                            
                            #handle field dump
                            value = lesson.get(field)
                            if str(value).lower() == "n/a" or not value: continue #skip empty values 
                            
                            if noduplicates and value in out: continue
                            out.append(value)
                            
                
                logger.ok(f"Exported data for {len(out)} lessons across {len(self.ScheduleDB.data_keyed.keys())} classes")
                
                if field == "*":
                    open("dump.txt", "w", encoding="utf-8").write(json.dumps(out, indent=4, ensure_ascii=False))
                    return
                
                open("dump.txt", "w", encoding="utf-8").write("\n".join(out))
                return
            logger.warn(f"Unknown field, available: subject, teacher, classroom, raw, *")
    
    def onStart(self, registry):
        self.running = True
        
        self.thread = Thread(target=self.update_schedule)
        self.thread.start()
        logger.ok("Started schedule manager")
        
    def onClose(self, reason):
        self.running = False
        if self.thread:
            self.thread.join(30)
        logger.ok("Stopped schedule manager")
    
    def update_schedule(self):
        while self.running:
            if time.time() < self.next_update:
                time.sleep(1/4)
                continue
            
            self.next_update = time.time() + self.update_period
            Config("vki")["persist.scheduleNextUpdate"] = self.next_update
            
            try:
                logger.info("Updating time tables from remote...")
                start = time.time()
                
                out = {}
                for schedule in NSUTablesUtil().getAllSchedules():
                    logger.debug(f"Fetched schedule for '{schedule.className}'")
                    out[schedule.className] = schedule
                
                # download_timetables()
                logger.ok(f"Updated {len(out.keys())} timetables, took {time.time()-start:.1f}s")
            except Exception as err:
                logger.trace(err)
                self.error = Messages.SCHEDULE_DOWNLOAD_ERROR.value
                continue
            
                
            try:
                self.create_diff(out)
            except Exception as err:
                logger.trace(err)
                self.error = Messages.SCHEDULE_DIFF_GEN_ERROR.value
                continue
            
            self.last_update = time.time() 
            self.error = None
            
        logger.warn(f"ScheduleManager update thread exited")
        
    def create_diff(self, schedule: dict):
        if not schedule:
            return

        #determine the new week's firstDay from any entry in the parsed schedule
        sample = next(iter(schedule.values()))
        new_first_day = sample.to_dict()["firstDay"]

        existing = self.ScheduleDB.filter(lambda _: True)
        is_new_week = not existing or existing[0].get("firstDay") != new_first_day

        if is_new_week:
            logger.info(f"New week detected (firstDay={new_first_day}), rebuilding schedule DB")
            for item in existing:
                self.ScheduleDB.removeByKey(item["className"])
            for week in schedule.values():
                self.ScheduleDB.create(**week.to_dict())
            return

        #compute diffs relative to the original (start-of-week) state
        for class_name, week in schedule.items():
            stored = self.ScheduleDB.getByKey(class_name)

            if stored is None:
                self.ScheduleDB.create(**week.to_dict())
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
                    for attr in ("subject", "teacher", "classroom"):
                        new_val = new_lesson.to_dict()[attr]
                        new_lesson.isCancelled = new_val in ["N/A", None] and attr == "subject"
                        
                        #baseline is the original value from the start of the week,
                        #not the most recently stored value (to preserve change history correctly)
                        baseline = stored_changes[attr][0] if attr in stored_changes else stored_lesson.get(attr)
                        if new_val != baseline:
                            changes[attr] = [baseline, new_val]

                    new_lesson.changes = changes

            self.ScheduleDB.setByKey(class_name, "days", [d.to_dict() for d in week.days])
        
Service.Export(ScheduleRunner, depends_on=["VKIConfig", "XelDB"])