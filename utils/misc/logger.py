import traceback
import datetime, os

class Logging:
    def __init__(self, appdata):
        self.logFolder = appdata+r"\logs"
        self.logFile = None
        if not os.path.exists(self.logFolder):
            os.mkdir(self.logFolder)

    def createLog(self, types, log_content):
        try:
            if self.logFile == None:
                self.logFile = self.logFolder+f"\\{str(datetime.datetime.now()).replace(':','-')}.log"
                with open(file=self.logFile, mode='w') as f:
                    f.write(f'[Log File CSGORPC | {datetime.datetime.now()}]')
                    f.close()

            with open(file=self.logFile, mode='w') as f:
                f.write('\n')
                f.write(f"[{datetime.datetime.now()}] {{{types}}} | {log_content}")
                f.close()
        except:    
            print('Unable to Create Log File')
            input('Press enter to exit')
            os._exit(1)