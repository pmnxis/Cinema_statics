from cinema import *
from csv2tplist import csv2tplist
from pytz import timezone
import codecs
import time

KST = timezone('Asia/Seoul')

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
        report = print_lines('-', 100, False) + '\n'
        report += '< Cinema Today Statics >\n'
        report += "기준 일자 : %04d년 %02d월 %02d일 | 생성 시간 : %02d시 %02d분 %02d초\n" % (now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec)
        report += "조회된 영화관 개수 : %d\n\n" % (len(self.cinemas))
        return report

    def proc(self):
        self.reports=''
        self.reports += self.get_report_head()
        for i in range(len(self.cinemas)):
            job = self.cinemas[i]
            job.get_data()
            job.parse_info()
            job.parse_table()
            job.gen_minmax_time()

        for i in range(len(self.cinemas)):
            report = ''
            report += print_lines('-', 100, False) + '\n'
            job = self.cinemas[i]
            report += job.print_table(False)
            self.reports += report
        
        self.reports += print_lines('-', 100, False) + '\n'

    def save_report_txt(self, dirpath = './'):
        now = time.localtime()
        file_name = dirpath + "CineStatics - %04dy%02dm%02dd.txt" % (now.tm_year, now.tm_mon, now.tm_mday)
        f = codecs.open(file_name, 'w', 'UTF-8-SIG')
        f.write(self.reports)
        f.close()
