

batterPos = ['c', '1b', '2b', 'ss', '3b','of1','of2','of3','util']
pitcherPos = ['sp1','sp2','sp3','sp4','sp5','rp1','rp2','p']

class Player:
    def __init__(self,name,dbid,pos):
        self.name = name
        self.dbid = dbid
        self.pos = Set(pos)
        
class Team:
    def __init__(self, name, owner, batters, batter_bench, pitchers, pitcher_bench):
        # __init__(self, name, owner, batters, batter_bench, pitchers, pitcher_bench)
        #    batters - list of Players (batting starters) in order of batter_pos
        #    batters_bench - list of batting bench Players
        #    pitchers - list of Players (pitching starters) in order of pitcher_pos
        #    pitcher_bench - list of pitching bench Players

        for ii in range(len(batters)):
            self.starters[params.batterPos[ii]] = batters[ii]
        for ii in range(len(pitchers)):
            self.starters[params.pitcherPos[ii]] = pitchers[ii]

        self.batter_bench = batter_bench
        self.pitcher_bench = pitcher_bench

        self.name = name
        self.owner = owner

        return
        
class League:
    def __init__(self,teams):
        self.teams = t
        

        
