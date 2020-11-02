from cinema_statics import *
from datetime import datetime, timedelta, date
import os
import shutil
from multiprocessing import Process, Lock, Queue
import math
import time

#error 
#Error Occured : 2020-06-10
#Error Occured : 2020-06-08

def doStuff(y, m , d):
    dd = date(y, m , d)
    #try:
    test = cinema_statics()
    test.add_bulk()
    test.proc(dd)
    test.save_report_txt('./reports/backup/')
    print('Done %s', dd.isoformat())
    #except:
    #    print('Error Occured : %s' % (dd.isoformat()))
    return


doStuff(2020,6,10)
doStuff(2020,6,8)

print('\n----Finish---sd-')
