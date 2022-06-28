import datetime

today = datetime.date.today().strftime("%y")
today = datetime.date.today().strftime("%m")

x = 50
sx = str(x).zfill(5)

print(sx)


# print(today)