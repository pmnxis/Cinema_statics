from cinema_statics import *
import os
import shutil

test = cinema_statics()
test.add_bulk()
test.proc()
pwd = './reports/'
for path, dirs, files in os.walk(pwd):
        for file in files:
            if(path == pwd):
                relpath = os.path.join(path, file)
                newpath = os.path.join(path+'backup/', file)
                shutil.move(relpath, newpath)
            
test.save_report_txt('./reports/')
print('\n----Finish----')
