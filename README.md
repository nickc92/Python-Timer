# Python-Timer

I always liked the Java Timer/TimerTask classes, and found them to be a
useful pattern in many applications.  Python seems to lack something quite
like this, so I implemented something simple in Python to do basically the
same thing.

    import Timer, time

    timer = Timer.Timer()
    class MyTask(Timer.TimerTask):
        def run(self):
	    print 'task running; current time is %.3f'%(time.time())

    task = MyTask()
    timer.schedulePeriodic(task, 1.0)
    time.sleep(10.0)
    
