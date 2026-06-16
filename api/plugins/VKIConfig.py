from nautica import Service, Config, ConfigBuilder

class VKIConfig(Service):
    def onInstall(self):
        Config.New("vki",
            ConfigBuilder()
                .add("encryptionKey", "", "Generate using 'users.keygen' in shell")
                
                .add("schedules.updateInterval", 600)
                .add("schedules.maxConcurrentRequests", 50)

                .add("grades.updateInterval", 600)
                .add("grades.maxConcurrentRequests", 5)
                
                .add("persist.scheduleNextUpdate", 0, "auto-generated, don't change")
                .build()
        )
        
Service.Export(VKIConfig)