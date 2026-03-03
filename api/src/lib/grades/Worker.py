import time
import asyncio
from threading import Thread

from nautica.api import MongoDB, Eventer, Config
from nautica.services.logger import LogManager
from nautica.services.database.xeldb import XelDB

from src.lib.NsuAPI import NsuAPI, NsuAPIError
from src.lib.Users import fernet

GradesCache = XelDB("Cache-Grades", primary_key="userId")
logger = LogManager("Lib.Grades.Worker")


class GradesWorker:
    def __init__(self):
        self.running = False
        self.thread = None
        self._refreshing: set[str] = set()  #inflight user ids (dedup)

    def start(self):
        self.running = True
        self.thread = Thread(target=lambda: asyncio.run(self._run()), daemon=True)
        self.thread.start()
        logger.ok("Started grades worker")

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(30)
        logger.ok("Stopped grades worker")

    async def _run(self):
        next_run = 0
        while self.running:
            if time.time() < next_run:
                await asyncio.sleep(0.25)
                continue

            next_run = time.time() + Config("vki")["grades.updateInterval"]
            try:
                await self._fetch_all()
            except Exception as err:
                logger.trace(err)

    async def _fetch_all(self):
        users = list(MongoDB("vki").users.find({}))
        if not users:
            return

        logger.info(f"Refreshing grades for {len(users)} users...")
        semaphore = asyncio.Semaphore(Config("vki")["grades.maxConcurrentRequests"])

        results = await asyncio.gather(
            *[self._fetch_user(u, semaphore) for u in users],
            return_exceptions=True,
        )

        ok = sum(1 for r in results if r is True)
        logger.ok(f"Grades refresh done: {ok}/{len(users)} succeeded")

    async def _fetch_user(self, user_doc: dict, semaphore: asyncio.Semaphore) -> bool:
        async with semaphore:
            return await self._do_fetch(user_doc)

    #single-user refresh (called from endpoint)----------

    async def refresh_user(self, user_doc: dict):
        """Fire-and-forget a single-user refresh. Skips if already in-flight."""
        uid = user_doc.get("_id")
        if uid in self._refreshing:
            return
        self._refreshing.add(uid)
        try:
            await self._do_fetch(user_doc)
        except Exception as err:
            logger.trace(err)
        finally:
            self._refreshing.discard(uid)

    #core fetch-----

    async def _do_fetch(self, user_doc: dict) -> bool:
        uid = user_doc.get("_id")
        email = user_doc.get("email")
        enc_password = user_doc.get("password")

        if not email or not enc_password:
            return False

        try:
            password = fernet.decrypt(enc_password.encode()).decode()
        except Exception:
            return False

        try:
            cookies, error = await NsuAPI.login(email, password)
            if error:
                logger.warn(f"Login failed for {uid}: {error}")
                return False

            api = NsuAPI(cookies)
            semester = await api.get_latest_semester()
            grades = await api.get_grades(semester)
        except NsuAPIError as err:
            logger.warn(f"Grade fetch failed for {uid}: {err}")
            return False

        serialized = [g.to_dict() for g in grades]

        cache_key = f"{uid}_sem{semester}"
        if GradesCache.getByKey(cache_key):
            GradesCache.setByKey(cache_key, "semester", semester)
            GradesCache.setByKey(cache_key, "grades", serialized)
            GradesCache.setByKey(cache_key, "fetchedAt", time.time())
        else:
            GradesCache.create(userId=cache_key, semester=semester, grades=serialized, fetchedAt=time.time())

        latest_key = f"{uid}_latest"
        if GradesCache.getByKey(latest_key):
            GradesCache.setByKey(latest_key, "semester", semester)
        else:
            GradesCache.create(userId=latest_key, semester=semester)

        return True


Worker = GradesWorker()


@Eventer.on("shutdown")
def on_shutdown(reason: str = None):
    Worker.stop()
