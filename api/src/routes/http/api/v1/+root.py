from src.lib.schedule.Runner import Schedules
from src.lib.grades.Worker import Worker as GradesWorker
from nautica.api import Eventer


Schedules.start()

@Eventer.on("database.ready")
def on_ready(*args, **kwargs):
    GradesWorker.start()