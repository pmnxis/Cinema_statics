from datetime import date, time, datetime
import requests
from bs4 import BeautifulSoup
import copy


getter_adr = 'http://www.kobis.or.kr/kobis/business/mast/thea/findShowHistorySc.do'
judge_dawn = time(4, 0)

def get_csrf():
    req = requests.get(getter_adr)
    html = req.text
    soup = BeautifulSoup(html, 'html.parser')
    csrf_token = soup.find('input', {'name':'CSRFToken'})['value']
    return csrf_token

def gen_post_form(csrf=get_csrf(), theaCd='', sTheaNm='', \
    tdstart=date.today().isoformat(), tdend=date.today().isoformat() ):
    theater_num = ''
    theater_str = ''
    if len(theaCd) == 0 and len(sTheaNm) != 0:
        # Get
        print('Not Implemented - Zero Theater Code Num')
    elif len(theaCd) != 0 and len(sTheaNm) == 0:
        theater_num = theaCd
        theater_str = '영화관'
    elif len(theaCd) != 0 and len(sTheaNm) != 0:
        theater_num = theaCd
        theater_str = sTheaNm
    else:
        print('Cannot Get any information from upper function.')
        
    data = {
        'CSRFToken': csrf,
        'theaCd': theater_num,
        'theaArea': 'Y',
        'showStartDt': tdstart,
        'showEndDt': tdend,
        'sWideareaCd':'',
        'sBasareaCd':'',
        'sTheaCd':'',
        'choice':'2',
        'sTheaNm':theater_str
    }
    return data

def isDateCombined(strline):
    sptline = strline.split('-')
    deto = []
    if(len(sptline) != 3):
        return False, False
    for i in range(3):
        try:
            temp = int(sptline[i])
            deto.append(temp)
        except ValueError:
            return False, False

    return True, date(deto[0], deto[1], deto[2])

def cleanMovieName(__text):
    if(len(__text) == 0):
        return __text
    __text = __text.replace('(디지털)', '')
    __text = __text.replace('(IMAX)', '')
    __text = __text.replace(',', '')
    __text = __text.replace('00원)', '^)')

    a = __text.find('(', 0, 4)
    b = __text.find('^)', a, a+9)
    if(a != -1 and b != -1):
        __text = __text[b+2:]
    

    if(__text[0] == ' '):
        __text = __text[1:]

    a = __text.find('(')
    if(a != -1):
        temp = __text.split('(')
        __text = copy.copy(temp[0])

    condition = False

    while condition:
        condition = False

        if(__text[0] == ' '):
                condition = True
                __text = __text[1:]
        
        if(__text[-1] == ' '):
                condition = True
                __text = __text[:-1]

    return __text

def parseMovieName(__text):
    stime = __text[:5]
    movie_title = __text[5:]
    movie_title = cleanMovieName(movie_title)
    
    temp = stime.split(':')
    hh = -1
    mm = -1
    stime_avail = True

    try:
        hh = int(temp[0])
        mm = int(temp[1])
    except ValueError:
        stime_avail = False
    
    ttime = False

    if stime_avail:
        if(hh>=24):
            print('OverTime Detected : %s | %s' %( stime, movie_title))
            hh -= 24
        ttime = time(hh, mm)

    return movie_title, ttime

def getMovieRunningTime(movie_name):
    # implemented yet.
    return 120

def autofindInList(lst, target):
    ret = -1
    for i in range(len(lst)):
        if(lst[i] == target):
            return i
        if(len(lst[i]) == 0 and ret == -1):
            ret = i
    if(ret == -1):
        lst.append(copy.copy(target))
        return len(lst) - 1
    else:
        lst[ret] = copy.copy(target)
        return ret

def cleanRoomName(name):
    temp = name.split('(')
    name = copy.copy(temp[0])
    name = name.encode('ascii', 'ignore')
    name = name.decode('utf-8')
    condition = False

    while condition:
        condition = False

        if(name[0] == ' '):
                condition = True
                name = name[1:]
        
        if(name[-1] == ' '):
                condition = True
                name = name[:-1]

    return name

def genListRoomMov(room_lst, lst):
    roomName = cleanRoomName(lst[0])
    roomIdx = autofindInList(room_lst, roomName)
    lst.pop(0)
    tmpLst = []
    for i in range(len(lst)):
        left , right = parseMovieName(lst[i])
        #tuple
        if(len(left) > 0 and right!=False):
            tmpLst.append((left, right))
    
    return roomIdx, tmpLst

def print_lines(_c , nr, doPrint=True):
    temp = ''
    for i in range(nr):
        temp += _c
    if doPrint:
        print(temp)
    return temp

class cinema:
    def __init__(self, name='', cidx='002266'):
        self.name = name
        self.cidx = cidx
        self.tdstart = date.today().isoformat()
        self.tdend= date.today().isoformat()
        self.room_data = []
        self.sch_fastest = []
        self.sch_latest = []
        self.sch_gap = []
    
    def get_data(self, tdstart = date.today().isoformat(), tdend = date.today().isoformat()):
        self.tdstart = tdstart
        self.tdend = tdend
        self.csrf = get_csrf()
        __post_form = gen_post_form(self.csrf, self.cidx, self.name, self.tdstart, self.tdend)
        __res = requests.post(getter_adr, data=__post_form)
        __html = __res.text
        __soup = BeautifulSoup(__html, 'html.parser')
        __table = __soup.find('table', {'class':'tbl3 info3'})
        self.data = [
            [
                [td.get_text(strip=True) for td in tr.find_all('td')] 
                for tr in __table.find_all('tr')
            ] 
            for __table in __soup.find_all('table')
        ]
        return self.data

    def parse_info(self):
        self.name       = copy.copy(self.data[0][0][0])
        self.category   = copy.copy(self.data[0][0][1])
        self.register   = copy.copy(self.data[0][1][1])
        self.address    = copy.copy(self.data[0][3][0])
        __idx = int(0)
        self.rooms_total_max = int(0)
        self.room_max_person = []
        self.room_names = []
        for i in range(0, len(self.data[1][1])):
            try:
                temp = int(self.data[1][1][i])
            except ValueError:
                continue
            if(temp > 0):
                self.room_max_person.append(temp)
                self.rooms_total_max += temp
                self.room_names.append('')

    def parse_table(self):
        core = self.data[2]
        temp_arr = []
        temp = []
        temp_date_arr = []
        __new_date = 0
        first = 0

        for i in range(len(core)):
            line = core[i]
            if(len(line) == 0):
                continue
            isDate , __new_date = isDateCombined(line[0])
            if isDate:
                left, right = genListRoomMov(self.room_names, line[1:])
                temp_date_arr.append(copy.copy(__new_date))
                if(first != 0):
                    temp_arr.append(copy.copy(temp))
                else:
                    first += 1
                temp = []
            else:
                left, right = genListRoomMov(self.room_names, line)
            
            temp.append((left,copy.copy(right)))
        
        if(len(temp) != 0):
            temp_arr.append(copy.copy(temp))
        


        self.room_data = temp_arr
        self.room_dates = temp_date_arr

    def gen_minmax_time(self):

        for i in range(len(self.room_data)):
            today_rooms = self.room_data[i]
            fastest = False
            latest = False
            faster = []
            later = []
            for j in range(len(today_rooms)):
                this_room = today_rooms[j]
                in_this_room = this_room[1]
                if(len(in_this_room) > 1):
                    fast_movie_time = in_this_room[0][1]
                    late_movie_time = in_this_room[-1][1]
                    faster.append(fast_movie_time)
                    later.append(late_movie_time)

                elif(len(in_this_room) == 1):
                    middle_movie_time = in_this_room[0][1]
                    if middle_movie_time < judge_dawn:
                        #dawn time
                        late_movie_time = middle_movie_time
                        later.append(late_movie_time)
                    else:
                        fast_movie_time = middle_movie_time
                        faster.append(fast_movie_time)

                else:
                    continue
            
            if(len(faster) != 0):
                fastest = faster[0]
                for i in range(1 , len(faster)):
                    if(faster[i] < fastest):
                        fastest = faster[i]

            if(len(later) != 0):
                latest = later[0]
                for i in range(1 , len(later)):
                    if judge_dawn < latest and judge_dawn < later[i]:
                        if(later[i] > latest):
                            latest = later[i]
                    elif judge_dawn < latest and judge_dawn > later[i]:
                        latest = later[i]
                    elif judge_dawn > latest and judge_dawn < later[i]:
                        continue
                    # judge_dawn > latest and judge_dawn > later[i]:
                    else:
                        if(later[i] > latest):
                            latest = later[i]

            #get Gap.
            gap = False
            if(fastest != False and latest != False):
                # lastest is less then 23:59
                if(latest > judge_dawn):
                    gap = datetime.combine(date.today(), latest) \
                        - datetime.combine(date.today(), fastest)
                    gap = int(gap.seconds)
                # if latest is in dawn, over 24:00
                else:
                    temp = time(0,0)
                    gl  = datetime.combine(date.today(), latest) \
                        - datetime.combine(date.today(), temp)

                    gf  = datetime.combine(date.today(), fastest) \
                        - datetime.combine(date.today(), temp)
                    
                    gap = int(gl.seconds) + int(gf.seconds)

            self.sch_fastest.append(fastest)
            self.sch_latest.append(latest)
            self.sch_gap.append(gap)
                

    def print_table(self, doPrint=True):
        rpt_txt = ''
        for i in range(len(self.room_data)):
            today_rooms = self.room_data[i]
            today_date = self.room_dates[i]
            __name = '{:<20s}'.format(self.name)
            date_print_str = 'Cinema : %s | Date : %s' % (__name, today_date.isoformat())
            rpt_txt += date_print_str + '\n'
            # Print Fastest, Latest, Gap
            fftime = self.sch_fastest[i].strftime('%H:%M')
            lltime = self.sch_latest[i].strftime('%H:%M')
            gptime = self.sch_gap[i]

            _m, _s = divmod(gptime, 60)
            _h, _m = divmod(_m, 60)
            __mins = int(gptime/60)
            gapstr = '%02d:%02d' % (_h, _m)
            played = 0
            for j in range(len(today_rooms)):
                this_room = today_rooms[j]
                in_this_room = this_room[1]
                played += len(in_this_room)
            statics_str = '*오픈시간 : % 5s\t *마감시간 : % 5s,\t *실 영업시간 : % 5s  <- {% 4d 분},\t 일일 상영회차 : %d' % (fftime, lltime, gapstr, __mins, played)
            rpt_txt += statics_str + '\n\n'

            for j in range(len(today_rooms)):
                this_room = today_rooms[j]
                in_this_room = this_room[1]
                room_name = self.room_names[this_room[0]]
                #plan_item = today_room[j]
                room_str = 'Room[% 3s] :% 2d <<\t' % (room_name, len(in_this_room))
                for k in range(len(in_this_room)):
                    peek_movie = in_this_room[k]
                    movie_title = peek_movie[0]
                    if(len(movie_title) > 6):
                        movie_title = movie_title[:6]
                    ttime = peek_movie[1]
                    hhmm_str = ttime.strftime('%H:%M')
                    peek_str = ' [% 5s-% 6s]\t' % (hhmm_str, movie_title)
                    room_str += peek_str
                rpt_txt += room_str + '\n'
            

        
        if doPrint:
            print(rpt_txt, end='')    
        self.reports = rpt_txt
        return self.reports
