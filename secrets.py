import mysql.connector-python

mydb = mysql.connector.connect(
    host = 'localhost',
    user = 'root',
    passwd = 'temppass',
    )

curr = mydb.cursor()

curr.execute("CREATE DATABASE cylinder1")

curr.execute("SHOW DATABASES")
for db in curr:
    print(db)