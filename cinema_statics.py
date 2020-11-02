from cinema import *
from csv2tplist import csv2tplist
from pytz import timezone
import codecs
import time
import os

KST = timezone('Asia/Seoul')

def __dateIsoformat(target):
    return (target.isoformat())[:10]


class cinema_statics:
    def __init__(self):
        self.cinema_txt_list = []
        self.cinemas = []

    def add(self, _name='', _cidx=''):
        self.cinema_txt_list.append((_name, _cidx))
        self.cinemas.append(cinema(name=_name, cidx=_cidx))
        #self.cinemas[-1].get_data()

    # gather from tuple list [(str,idx), (str,idx), (str,idx), ...]
    def add_bulk(self, tplst=csv2tplist('./cinema_list.csv')):
        for item in tplst:
            self.add(_name=item[0], _cidx=item[1])

    def get_report_head(self):
        now = time.localtime()
        nr_fail = self.failedJob
        nr_succ = len(self.cinemas) - nr_fail
        if self.specificDate == date.today():
            report = print_lines('-', 100, False) + '\n'
            report += '< Cinema Today Statics >\n'
            report += "기준 일자 : %04d년 %02d월 %02d일 | 생성 시간 : %02d시 %02d분 %02d초\n" % (now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec)
            report += "조회한 영화관 개수 : %d\n" % (len(self.cinemas))
        else:
            report = print_lines('-', 100, False) + '\n'
            report += '< Cinema Specific Statics >\n'
            report += '기준 일자 : %04d년 %02d월 %02d일 (당일날 조회한 데이터 아님, 과거 혹은 미래시점)\n' % (self.specificDate.year, self.specificDate.month, self.specificDate.day)
            report += "생성 일자 : %04d년 %02d월 %02d일 | 생성 시간 : %02d시 %02d분 %02d초\n" % (now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec)
            report += "조회한 영화관 개수 : %d\n" % (len(self.cinemas))\
        
        if nr_fail is not 0:
            report += "조회실패한 영화관이 있습니다.\n"
            report += "조회 성공 : %02d | 조회 실패 : %02d\n\n" % (nr_succ, nr_fail)
        else:
            report += "\n"

        return report

    def proc(self, specificDate=None):
        self.reports=''
        self.failedJob = int(0)
        if specificDate is None:
            self.specificDate = date.today()
        else:
            if(type(specificDate) == type(date.today())):
                self.specificDate = specificDate
            elif(type(specificDate) == type(datetime.now())):
                self.specificDate = specificDate.date()
            else:
                self.specificDate = date.today()
        
        #self.reports += self.get_report_head()

        for i in range(len(self.cinemas)):
            job = self.cinemas[i]
            if specificDate is None:
                job.get_data()
            else:
                job.get_data(tdstart=self.specificDate.isoformat(), tdend=self.specificDate.isoformat())
            job.parse_info()
            job.parse_table()
            job.gen_minmax_time()

        for i in range(len(self.cinemas)):
            report = ''
            report += print_lines('-', 100, False) + '\n'
            job = self.cinemas[i]
            report += job.print_table(False)
            if(job.isAvailable == False):
                self.failedJob += 1
            self.reports += report
        
        self.reports += print_lines('-', 100, False) + '\n'

        # head is genearted after parsed all.
        self.reports = self.get_report_head() + self.reports

    def save_report_txt(self, dirpath = './'):
        day = self.specificDate
        file_name = dirpath + "CineStatics - %04dy%02dm%02dd.txt" % (day.year, day.month, day.day)
        if os.path.exists(file_name):
            os.remove(file_name)
            print('%s is Already existed, remove it and recreate now', file_name)
        f = codecs.open(file_name, 'w', 'UTF-8-SIG')
        f.write(self.reports)
        f.close()
