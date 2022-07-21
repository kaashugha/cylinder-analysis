from datetime import date
import datetime
from dateutil.relativedelta import relativedelta

threed = date.today() + relativedelta(days=+3)

year = str(threed)[:-6]
month = str(threed)[5:-3]
day= str(threed)[8:]

print(threed)
print(year)
print(month)
print(day)
