from cinema_statics import *
from datetime import datetime, timedelta, date
import os
import shutil
from multiprocessing import Process, Lock, Queue
import math
import time

def dodo(que=Queue()):
    while que.empty() is False:
        try:
        dd = que.get()
        test = cinema_statics()
        test.add_bulk()
        test.proc(dd)
        test.save_report_txt('./reports/backup/')
        print('Done %s', dd.isoformat())
        except:
            print('Error Occured : %s' % (dd.isoformat()))
    return

def proc_day_div(_start, _end, nr_proc):
    que = Queue()
    for i in range(_start, _end):
        d = datetime.today() - timedelta(days=i)
        d = d.date()
        que.put(copy.copy(d))
    proc = []
    for i in range(nr_proc):
        proc.append(Process(target=dodo, args=(que,)))
        proc[i].start()
    
    que.close()
    que.join_thread()
    for i in range(nr_proc):
        proc[i].join()




proc_day_div(365, 365+31+3, 16)
    
print('\n----Finish---sd-')
