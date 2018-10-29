import time, threading

class TimerTask:
    def __init__(self):
        pass

    def schedule(self, **kw):
        tNow = time.time()
        self.timer = kw['timer']
        self.isPeriodic = kw.get('isPeriodic', False)
        self.periodSecs = kw.get('periodSecs', 0.0)
        delaySecs = kw.get('delaySecs', 0.0)
        self.nextRunTime = tNow + delaySecs

    def cancel(self):
        self.timer.cancelTask(self)

    def run(self):
        pass

class Timer:
    def __init__(self):
        self.waitTime = 1.0E9        
        self.taskList = []
        self.runEvent = False
        self.lock = threading.RLock()
        self.wakeEvent = threading.Event()
        self.runThread = threading.Thread(target=self.execThread)
        self.runThread.setDaemon(True)
        self.runThread.start()


    def execThread(self):
        while True:
            self.wakeEvent.wait(self.waitTime)
            self.wakeEvent.clear()
            try:
                self.lock.acquire()                
                self.taskList.sort(lambda x, y: cmp(x.nextRunTime, y.nextRunTime))

                tNow = time.time()

                if len(self.taskList) > 0 and tNow >= self.taskList[0].nextRunTime - 0.001:
                    task = self.taskList[0]
                    task.run()
                    if task.isPeriodic:
                        task.nextRunTime += task.periodSecs
                        self.taskList.sort(lambda x, y: cmp(x.nextRunTime, y.nextRunTime))
                    else:
                        self.taskList = self.taskList[1:]

                if len(self.taskList) > 0:
                    self.waitTime = self.taskList[0].nextRunTime - tNow
                    if self.waitTime < 0.0: self.waitTime = 0.0
                else:
                    self.waitTime = 1.0E9

            finally:
                self.lock.release()


    def cancelTask(self, task):
        self.lock.acquire()
        self.runEvent = False
        self.taskList = [x for x in self.taskList if x != task]
        self.lock.release()
        self.wakeEvent.set()        

    def cancel(self):
        self.lock.acquire()
        self.runEvent = False
        self.taskList = []
        self.lock.release()
        self.wakeEvent.set()

    def schedule(self, task, delaySecs):
        task.schedule(isPeriodic=False, timer=self, delaySecs=delaySecs)
        self.lock.acquire()
        self.taskList.append(task)
        self.runEvent = False
        self.lock.release()
        self.wakeEvent.set()

    def schedulePeriodic(self, task, periodSecs, delaySecs=0.0):
        task.schedule(isPeriodic=True, timer=self, delaySecs=delaySecs, periodSecs=periodSecs)
        self.lock.acquire()
        self.taskList.append(task)
        self.runEvent = False
        self.lock.release()
        self.wakeEvent.set()        
    
if __name__ == '__main__':
    timer = Timer()
    class MyTask1(TimerTask):
        def run(self):
            print 'task1 running; current time is %.3f'%(time.time())

    class MyTask2(TimerTask):
        def run(self):
            print 'task2 running; current time is %.3f'%(time.time())
            
    print 'did schedule at', time.time()
    task1 = MyTask1()
    timer.schedule(task1, 5.0)
    time.sleep(1.0)
    task1.cancel()
    time.sleep(6.0)
