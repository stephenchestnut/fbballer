import mysql.connector as mariadb

bball=mariadb.connect(user='root',password='',host='127.0.0.1',database='stats')
curs=bball.cursor()

curs.execute("SELECT * FROM batting WHERE (yearID='2015' AND lgID='NL');")
for x in curs:
    print(x)

curs.execute("SELECT * FROM pitching WHERE (yearID='2015' AND lgID='NL');")
for x in curs:
    print(x)

bball.close()

#[(a[0], [int(ii) for ii in a[5:]]) for a in x]
