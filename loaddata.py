import mysql.connector as mariadb

import params as p

def loaddata___connect():
    return mariadb.connect(user='root',password='',host='127.0.0.1',database='stats')

def batters():
    #connect to dbase and get the batters
    bball = loaddata___connect()
    curs = bball.cursor()

    B = dict()
    #load data for each year until max year, make it all numbers, put it in a map
    for year in range(p.minYear,p.maxYear+1):
        curs.execute("SELECT * FROM batting WHERE (yearID='" + str(year) + "' AND lgID='NL' AND G>" + str(p.minGames) + " AND AB>0);")
        x = curs.fetchall()
        Byear = [(a[0], [int(ii) for ii in a[5:]] +
                [1.0*(a[8]+a[15]+int(a[18]))/(a[6]+a[8]+a[15]+int(a[18])), #OBP
                 1.0*(a[8]+a[9]+2*a[10]+3*a[11])/a[6]])                     #SLG
             for a in x] 
        B[year]=Byear
        
    bball.close()

    return B

def pitchers():
    bball = loaddata___connect()
    curs = bball.cursor()
    
    curs.execute("SELECT * FROM pitching WHERE (yearID='2015' AND lgID='NL');")
    for x in curs:
        print(x)

    bball.close()

#[(a[0], [int(ii) for ii in a[5:]]) for a in x]
