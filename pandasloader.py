import mysql.connector as mariadb
import pandas

_batter_load_str = " AB>0 AND G>" + str(p.minGames) + " AND yearID>=" + str(params.minYear) + " AND yearID<=" + str(params.maxYear) + " "
_pitcher_load_str = " AND IPOuts>0 AND BFP>" + str(p.minBatters) + " AND yearID>=" + str(params.minYear) + " AND yearID<=" + str(params.maxYear) + " "

class LahmanDB(object):

    def __init__(self):
        self._batters_data=None
        self._pitchers_data=None
        self._players_data=None
        return

    def connect(self):
        self.bball = mariadb.connect(user='root',password='',host='127.0.0.1',database='stats')
        return

    def disconnect(self):
        self.bball.close()
        return

    def players(self):
        # Load player info
        # {'playerID':(birthYear,debut year,weight,height)} = lahman_players()

        if self._players_data==None:
            self._players_data = pandas.read_sql("SELECT playerID, birthYear, debut, weight, height FROM master", con=self.bball)
            
        return pandas.DataFrame.copy(self._players_data)

    def batters(self):
        if self._batters_data==None:
            dat = pandas.read_sql("SELECT playerID, R, HR, RBI, SB, G, AB, H, 2B, 3B, CS, BB, SO, IBB, HBP, SH, SF, GIDP FROM batting WHERE (" + _batter_load_str + " )")
            dat['OBP'] = (dat['H']+dat['BB']+dat['HBP'])/(dat['AB']+dat['BB']+dat['HBP']+dat['SF'])
            dat['SLG'] = (dat['H']+dat['2B']+dat['3B']*2.0+dat['HR']*3.0)/dat['AB']
            self._batters_data = dat
            
        return pandas.DataFrame.copy(self._batters_data)

    def pitchers(self):
        if self._pitchers_data==None:
            dat = pandas.read_sql("SELECT playerID,W,SV,SO,ERA,H,BB,IPOuts,HBP,IBB,L,G,GS,CG,SHO,ER,HR,WP,BK,BFP,GF,R FROM pitching WHERE ("+ _batter_load_str +");")
            dat['WHIP'] = (dat['W'] + dat['H']) / dat['IPOuts']
            dat['QS'] = 1
            self._pitchers_data = dat

        return pandas.DataFrame.copy(self._pitchers_data)
