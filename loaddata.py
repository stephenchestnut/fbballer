import mysql.connector as mariadb

import params as p
import numpy as np

###################
# Batters data in the form:
# [((playerID,year), (score, OBP, SLG, R, HR, RBI, SB, G, AB, H, 2B, 3B, CS, BB, SO, IBB, HBP, SH, SF, GIDP, age, years played, weight, height))]
# Score of a player in year is sum of his normalized OBP,SLG,R,HR,RBI,SB
###################
def batters():
    #Load and standardize data for all batters
    #[ ((playerID,year),(score,s,t,a,t,s))] = batters()

    def blfun(year,WHERE=""):
        return loaddata___batters(year,WHERE+" AND G> " + str(p.minGames) + " ")

    return loaddata___datasetup(blfun)

###################
# Pitchers data in the form:
# [((playerID,year), (score, W, SV, SO, -ERA, -WHIP, QS(=1), H, BB, IPOuts, HBP, IBB, L, G, GS, CG, SHO, ER, HR, BAOpp, WP, BK, BFP, GF, age, years played, weight, height))]
# Score of a player in year is sum of his normalized OBP,SLG,R,HR,RBI,SB
###################
def pitchers():
    #Load and standardize data for all pitchers
    #[ ((playerID,year),(score,s,t,a,t,s))] = pitchers()

    def pifun(year,WHERE=""):
        return loaddata___pitchers(year,WHERE+" AND BFP>" + str(p.minBatters) + " ")

    return loaddata___datasetup(pifun)

####################
#Load 2015 NL batters data with scores computed from 2015 data
#Format is the same as batters()
####################
def NLBatters2015():
    return loaddata___datasetup(loaddata___NLBatters2015,styear=2015,enyear=2015)

####################
#Load 2015 NL pitchers data with scores computed from 2015 data
#Format is the same as pitchers()
####################
def NLPitchers2015():
    return loaddata___datasetup(loaddata___NLPitchers2015,styear=2015,enyear=2015)

####################
# Player identification data for NL 2015
# {playerID:(nameFirst,nameLast,Pos)} for 2015 NL players 
####################
def NLNames2015():
    bball=loaddata___connect()
    curs=bball.cursor()

    curs.execute("SELECT playerID,nameFirst,nameLast FROM master;")
    names = curs.fetchall()
    namedict = dict([(x[0], x[1:]) for x in names])

    curs.execute("SELECT playerID,Pos FROM fielding WHERE (yearID=2015 AND lgID='NL');")
    pos = curs.fetchall()
    bball.close()

    unknowns = ['annade01', 'diazel01', 'lombast02', 'waldrky02']
    q = ['?','?','?','?']
    return dict([(x[0], namedict[x[0]] + x[1:]) for x in pos] + list(zip(unknowns,zip(q,q,q))))
    
    
########################
### Helper functions ###
########################
def loaddata___battersWHERE():
    #Restriction on batter selection from database
    return  " AB>0 "

def loaddata___pitchersWHERE():
    #Restriction on pitcher selection from database
    return  " IPOuts>0 "

def loaddata___connect():
    #Connect to the database
    return mariadb.connect(user='root',password='',host='127.0.0.1',database='stats')

def loaddata___players():
    # Load player info
    # {'playerID':(birthYear,debut year,weight,height)} = loaddata___players()
    bball = loaddata___connect()
    curs = bball.cursor()

    curs.execute("SELECT playerID, birthYear, debut, weight, height FROM master")
    x = curs.fetchall()
    return dict([(a[0],(a[1],int(a[2][0:4]),a[3],a[4])) for a in x if a[2]!=''])


def loaddata___datasetup(load_year,styear=p.minYear,enyear=p.maxYear):
    # load and normalize data for all of the years, add player data

    dat=[]
    pl = loaddata___players()
    
    #Get last year data and compute scores
    datyear = load_year(enyear+1)

    #normalize the six scoring categories, compute scores and store them
    scorecats = [x[1][0:6] for x in datyear] 
    norm = np.percentile(scorecats,p.normPct,axis=0)

    #score is sum of normalized categories
    scores = dict([ #{(playerID,year):float score}
        ( (x[0],enyear+1), sum([1.0*x[1][i] / norm[i] for i in range(0,6)]) )
        for x in datyear]) 
    
    for year in range(enyear,styear-1,-1):
        datyear = load_year(year)
        scorecats = [x[1][0:6] for x in datyear] 
        norm = np.percentile(scorecats,p.normPct,axis=0)
        scores.update([
            ( (x[0],year), sum([1.0*x[1][i] / norm[i] for i in range(0,6)]) )
            for x in datyear])
        dat = dat + [((x[0],year),
                  (scores[(x[0],year+1)],) + #next year's score
                  x[1] +
                  (year-pl[x[0]][0],   #age
                   year-pl[x[0]][1]) + #years in league
                   pl[x[0]][2:])
                 for x in datyear if ( (x[0] in pl) and ((x[0],year+1) in scores) )]
    return dat

def loaddata___batters(year,WHERE=""):
    #Load batter performance by year
    #[(playerID,(s,t,a,t,s))] = load_batters(year)
    #[(playerID,(s,t,a,t,s))] = load_batters(year,WHERE=" AND lgID='NL'")
    
    #connect to dbase and get the batters
    bball = loaddata___connect()
    curs = bball.cursor()

    #load data for each year until max year, make it all numbers, put it in a map
    curs.execute("SELECT playerID, R, HR, RBI, SB, G, AB, H, 2B, 3B, CS, BB, SO, IBB, HBP, SH, SF, GIDP FROM batting WHERE (" + loaddata___battersWHERE() + " AND yearID=" + str(year) + WHERE + ");")
    entries = curs.fetchall()
    B = [(
        a[0],
        #OBP: (H+BB+HBP)/(AB+BB+HBP+SF)
        ((1.0*a[7]+a[11]+int(a[14]))/(a[6]+a[11]+int(a[14])+int(a[16])),
         #SLG: (H+2B+2*3B+3*HR)/AB
        (1.0*a[7]+a[8]+2*a[9]+3*a[2])/a[6]) +  
        a[1:13] +
        tuple([int(x) for x in a[13:]]))
        for a in entries]
        
    bball.close()

    return B

def loaddata___pitchers(year, WHERE=""):
    # Raw pitcher data from the database
    #[(playerID,(s,t,a,t,s))] = loaddata___pitchers(year)
    #[(playerID,(s,t,a,t,s))] = loaddata___pitchers(year, WHERE=" AND lgID='NL')
    
    bball = loaddata___connect()
    curs = bball.cursor()
    
    curs.execute("SELECT playerID,W,SV,SO,ERA,H,BB,IPOuts,HBP,IBB,L,G,GS,CG,SHO,ER,HR,WP,BK,BFP,GF,R FROM pitching WHERE (yearID="+str(year)+" AND " + loaddata___pitchersWHERE() + WHERE + ");")
    entries = curs.fetchall()
    P = [(
        x[0],
        x[1:4] + 
        (-1.0*x[4], #-ERA
         -1.0*(x[6]+x[5])/x[7], #-WHIP
         1) +  #Quality starts (don't have data currently)
        tuple([float(i) for i in x[5:]]))
         for x in entries]
    bball.close()
    return P

def loaddata___NLBatters2015(year):
    return loaddata___batters(2015,WHERE=" AND lgID='NL'")

def loaddata___NLPitchers2015(year):
    return loaddata___pitchers(2015,WHERE=" AND lgID='NL'")
