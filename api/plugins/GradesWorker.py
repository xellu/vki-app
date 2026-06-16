import time
import asyncio
from threading import Thread

from nautica import Logger, Config, Service, Services

from plugins.NsuAPI import NsuAPI, NsuAPIError
from src.lib.Users import UserManager
from src.lib.Mongo import Mongo

from plugins.XelDB import XelDB

class GradesWorker(Service):
    def __init__(self):
        super().__init__()
        
        self.running = False
        self.thread = None
        self._refreshing: set[str] = set()  #inflight user ids (dedup)
        
        self.gradesCache: XelDB.Instance = None

    def onSetup(self, registry):
        self.gradesCache = Services["XelDB"].create("Cache-Grades", primary_key="userId")

    def onStart(self, registry):
        self.running = True
        self.thread = Thread(target=lambda: asyncio.run(self._run()), daemon=True)
        self.thread.start()
        Logger.ok("Started grades worker")

    def onClose(self, reason):
        self.running = False
        if self.thread:
            self.thread.join(30)
        Logger.ok("Stopped grades worker")

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
                Logger.trace(err)

    async def _fetch_all(self):
        users = list(Mongo("vki").users.find({}))
        if not users:
            return

        Logger.info(f"Refreshing grades for {len(users)} users...")
        semaphore = asyncio.Semaphore(Config("vki")["grades.maxConcurrentRequests"])

        start = time.time()
        results = await asyncio.gather(
            *[self._fetch_user(u, semaphore) for u in users],
            return_exceptions=True,
        )

        ok = sum(1 for r in results if r is True)
        Logger.ok(f"Grades refresh done: {ok}/{len(users)} succeeded, took {time.time()-start:.2f}s")

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
            Logger.trace(err)
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
            password = UserManager.get_fernet().decrypt(enc_password.encode()).decode()
        except Exception:
            return False

        try:
            cookies, error = await NsuAPI.login(email, password)
            if error:
                Logger.warn(f"Login failed for {uid}: {error}")
                return False

            api = NsuAPI.getClient(cookies)
            semester = await api.get_latest_semester()
            grades = await api.get_grades(semester)
        except NsuAPIError as err:
            Logger.warn(f"Grade fetch failed for {uid}: {err}")
            return False

        serialized = [g.to_dict() for g in grades]

        cache_key = f"{uid}_sem{semester}"
        if self.gradesCache.getByKey(cache_key):
            self.gradesCache.setByKey(cache_key, "semester", semester)
            self.gradesCache.setByKey(cache_key, "grades", serialized)
            self.gradesCache.setByKey(cache_key, "fetchedAt", time.time())
        else:
            self.gradesCache.create(userId=cache_key, semester=semester, grades=serialized, fetchedAt=time.time())

        latest_key = f"{uid}_latest"
        if self.gradesCache.getByKey(latest_key):
            self.gradesCache.setByKey(latest_key, "semester", semester)
        else:
            self.gradesCache.create(userId=latest_key, semester=semester)

        return True
    
Service.Export(GradesWorker, depends_on=["MongoDB", "XelDB", "VKIConfig"])