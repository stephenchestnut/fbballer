import mysql.connector as mariadb

import params as p
import numpy as np
import value


class LahmanDB(object):
    def __init__(self):
        return
    
    def connect(self):
    #Connect to the database
        self.bball = mariadb.connect(user='root',password='',host='127.0.0.1',database='stats')
        return
        
    def disconnect(self):
        self.bball.close()
        return

    def players(self):
        # Load player info
        # {'playerID':(birthYear,debut year,weight,height)} = lahman_players()
        curs = self.bball.cursor()

        curs.execute("SELECT playerID, birthYear, debut, weight, height FROM master")
        x = curs.fetchall()
        curs.close()
        
        return dict([(a[0],(a[1],int(a[2][0:4]),a[3],a[4])) for a in x if a[2]!=''])
    
    ###################
    # Batters data in the form:
    # [((playerID,year), (score, OBP, SLG, R, HR, RBI, SB, G, AB, H, 2B, 3B, CS, BB, SO, IBB, HBP, SH, SF, GIDP, age, years played, weight, height))]
    # Score of a player in year is sum of his normalized OBP,SLG,R,HR,RBI,SB
    ###################
    def batters(self,styear=p.minYear, enyear=p.maxYear):
        #Load and standardize data for all batters
        #[ ((playerID,year),(score,s,t,a,t,s))] = batters()
    
        def blfun(year,WHERE=""):
            return self._batter_query(year,WHERE+" AND G> " + str(p.minGames) + " ")

        return self._datasetup(blfun, styear, enyear)

    ###################
    # Pitchers data in the form:
    # [((playerID,year), (score, W, SV, SO, -ERA, -WHIP, QS(=1), H, BB, IPOuts, HBP, IBB, L, G, GS, CG, SHO, ER, HR, BAOpp, WP, BK, BFP, GF, age, years played, weight, height))]
    # Score of a player in year is sum of his normalized OBP,SLG,R,HR,RBI,SB
    ###################
    def pitchers(self,styear=p.minYear,enyear=p.maxYear):
        #Load and standardize data for all pitchers
        #[ ((playerID,year),(score,s,t,a,t,s))] = pitchers()
        
        def pifun(year,WHERE=""):
            return self._pitcher_query(year,WHERE+" AND BFP>" + str(p.minBatters) + " ")

        return self._datasetup(pifun, styear, enyear)
        
    def _battersWHERE(self):
        #Restriction on batter selection from database
        return  " AB>0 "

    def _pitchersWHERE(self):
        #Restriction on pitcher selection from database
        return  " IPOuts>0 "

    def _datasetup(self,load_year,styear=p.minYear,enyear=p.maxYear):
        # load and normalize data for all of the years, add player data
        
        dat=[] #list for cumulative data of all years
        pl = self.players()
        
        #Get last year data and compute scores
        datyear = load_year(enyear+1)
        
        #normalize the six scoring categories, compute scores and store them
        scorecats = [x[1][0:6] for x in datyear]
        vals = value.normalize_stats(scorecats)
        
        #score is sum of normalized categories
        scores = dict([ #{(playerID,year):float score}
            ( (datyear[ii][0],enyear+1), vals[ii] )
            for ii in range(len(datyear))]) 
        
        for year in range(enyear,styear-1,-1):
            datyear = load_year(year)
            scorecats = [x[1][0:6] for x in datyear] 
            vals = value.normalize_stats(scorecats)
            scores.update([
                ( (datyear[ii][0],year), vals[ii] )
                for ii in range(len(datyear))])
            dat = dat + [((x[0],year),
                          (scores[(x[0],year+1)],) + #next year's score
                          x[1] +
                          (year-pl[x[0]][0],   #age
                           year-pl[x[0]][1]) + #years in league
                          pl[x[0]][2:])
                         for x in datyear if ( (x[0] in pl) and ((x[0],year+1) in scores) )]
        return dat

    def _batter_query(self,year,WHERE=""):
        #Load batter performance by year
        #[(playerID,(s,t,a,t,s))] = lahman_batter_query(year)
        #[(playerID,(s,t,a,t,s))] = lahman_batter_query(year,WHERE=" AND lgID='NL'")
        
        #connect to dbase and get the batters
        curs = self.bball.cursor()

        #load data for each year until max year, make it all numbers, put it in a map
        curs.execute("SELECT playerID, R, HR, RBI, SB, G, AB, H, 2B, 3B, CS, BB, SO, IBB, HBP, SH, SF, GIDP FROM batting WHERE (" + self._battersWHERE() + " AND yearID=" + str(year) + WHERE + ");")
        entries = curs.fetchall()
        curs.close()
        B = [(
            a[0],
            #OBP: (H+BB+HBP)/(AB+BB+HBP+SF)
            ((1.0*a[7]+a[11]+int(a[14]))/(a[6]+a[11]+int(a[14])+int(a[16])),
             #SLG: (H+2B+2*3B+3*HR)/AB
             (1.0*a[7]+a[8]+2*a[9]+3*a[2])/a[6]) +  
            a[1:13] +
            tuple([int(x) for x in a[13:]]))
             for a in entries]

        return B

    def _pitcher_query(self,year, WHERE=""):
        # Raw pitcher data from the database
        #[(playerID,(s,t,a,t,s))] = lahman_pitcher_query(year)
        #[(playerID,(s,t,a,t,s))] = lahman_pitcher_query(year, WHERE=" AND lgID='NL')
        
        curs = self.bball.cursor()
    
        curs.execute("SELECT playerID,W,SV,SO,ERA,H,BB,IPOuts,HBP,IBB,L,G,GS,CG,SHO,ER,HR,WP,BK,BFP,GF,R FROM pitching WHERE (yearID="+str(year)+" AND " + self._pitchersWHERE() + WHERE + ");")
        entries = curs.fetchall()
        curs.close()
        P = [(
            x[0],
            x[1:4] + 
            (-1.0*x[4], #-ERA
             -1.0*(x[6]+x[5])/x[7], #-WHIP
             1) +  #Quality starts (don't have data currently)
            tuple([float(i) for i in x[5:]]))
             for x in entries]

        return P

class LahmanNL2015(LahmanDB):
    ####################
    #Load 2015 NL batters data with scores computed from 2015 data
    #Format is the same as batters()
    ####################
    def NLBatters2015(self):
        return self._datasetup(self._NLBatters2015_query,styear=2015,enyear=2015)

    ####################
    #Load 2015 NL pitchers data with scores computed from 2015 data
    #Format is the same as pitchers()
    ####################
    def NLPitchers2015(self):
        return self._datasetup(self._NLPitchers2015_query,styear=2015,enyear=2015)

    ####################
    # Player identification data for NL 2015
    # {playerID:(nameFirst,nameLast,Pos)} for 2015 NL players 
    ####################
    def NLNames2015(self):
        curs=self.bball.cursor()
        
        curs.execute("SELECT playerID,nameFirst,nameLast FROM master;")
        names = curs.fetchall()
        namedict = dict([(x[0], x[1:]) for x in names])
        
        curs.execute("SELECT playerID,Pos FROM fielding WHERE (yearID=2015 AND lgID='NL');")
        pos = curs.fetchall()
        curs.close()
        
        unknowns = ['annade01', 'diazel01', 'lombast02', 'waldrky02']
        q = ['?','?','?','?']
        return dict([(x[0], namedict[x[0]] + x[1:]) for x in pos] + list(zip(unknowns,zip(q,q,q))))

    def _NLBatters2015_query(self,year):
        return self._batter_query(2015,WHERE=" AND lgID='NL'")

    def _NLPitchers2015_query(self,year):
        return self._pitcher_query(2015,WHERE=" AND lgID='NL'")
