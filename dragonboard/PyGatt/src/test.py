import threading
import time

exitFlag = 0

class time_thread (threading.Thread):
    def __init__(self):
        super(time_thread, self).__init__()
        self._stop = threading.Event()
        self.status = None
    def run(self):
        print "Starting " 
        time.sleep(5)
        if self.status is None:
            sendError()
        print "Exiting " 
        
    def stop(self):
        self.status = 1
        self._stop.set()

def sendError():
    print "Error"

# Create new threads
thread = time_thread()

thread.start()

s = raw_input()
if s == '0':
    thread.stop()
    