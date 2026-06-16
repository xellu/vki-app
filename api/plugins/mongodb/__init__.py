from nautica import Service, Config, ConfigBuilder, Logger

import time
import threading
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo.collection import Collection
from pymongo.errors import ServerSelectionTimeoutError

class MongoDB(Service):
    def __init__(self):
        super().__init__()
        
        self.client: MongoClient | None = None
        self.thread = None
        
        self.is_connected = False
        
    def onInstall(self):
        Config.New("mongodb",
            ConfigBuilder()
                .add("url", "mongodb://localhost:27017", comment="MongoDB connection string")
                .add("database", "nautica", comment="Database name")
                .add("timeout", 5000, comment="Connection timeout (in ms)")
                .add("crashOnTimeout", True, comment="Stop the server if the database fails to connect")
                .build()
        )
    
    def onSetup(self, registry):
        Logger.info("Connecting to Mongo...")
        self.thread = t = threading.Thread(target=self._connect, daemon=True)
        t.start()
        
        start_time = time.time()
        timeout, timeoutWarn, timeoutError = Config("mongodb")["timeout"]/1000, False, False
        
        while True: #block main thread to prevent race conditions
            # Logger.debug(f"checking, {time.time() - start_time}, {timeout}")
            if self.is_connected:
                Logger.ok("Connection established")
                break
            
            if time.time() - start_time > timeout/2 and not timeoutWarn:
                Logger.warn("Connection is taking too long")
                timeoutWarn = True
                
            if time.time() - start_time >= timeout:
                Logger.error("Database failed to connect")
                timeoutError = True
                break

            time.sleep(1/5)
        
        if timeoutError and Config("mongodb")["crashOnTimeout"]:
            raise RuntimeError("MongoDB couldn't initialize")
    
    def onClose(self, reason):
        self.is_connected = False
        if self.client:
            self.client.close()
    
    def _connect(self) -> None:
        try:
            uri = Config("mongodb")["url"]    
            timeout = Config("mongodb")["timeout"]
            self.client = MongoClient(uri, server_api=ServerApi('1'), serverSelectionTimeoutMS=timeout)

            try:
                self.client.admin.command('ping')
                self.is_connected = True
                
            except ServerSelectionTimeoutError:
                self.is_connected = False
                Logger.error("Database failed to connect")
                return
                
            except Exception as e:
                self.is_connected = False
                Logger.trace(e)
                return


        except Exception as e:
            self.is_connected = False
            Logger.trace(e)
            return
        
    def __call__(self, collection) -> Collection:
        if not self.client:
            raise RuntimeError("MongoDB is not connected yet")
        
        return self.client.get_database(Config("mongodb")["database"]).get_collection(collection)
    
    
Service.Export(MongoDB)