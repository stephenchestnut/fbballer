import mysql.connector as mariadb

bball=mariadb.connect(user='root',password='',host='127.0.0.1',database='stats')
curs=bball.cursor()

curs.execute("SELECT * FROM batting WHERE (yearID='2015');")
for x in curs:
    print(x)
