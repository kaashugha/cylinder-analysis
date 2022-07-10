import datetime


cur_day = int(datetime.date.today().strftime("%d"))
cur_mo = int(datetime.date.today().strftime("%m"))
cur_year = int(datetime.date.today().strftime("%y"))

print (cur_day)
print (cur_mo)
print (cur_year)
