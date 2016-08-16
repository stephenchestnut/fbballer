import params
import numpy
import loaddata

########################################
## Class for building valuation tools ##
########################################

class Valuation(object):
    
    def __init__(self,db,year):
        return
    
    def batter_values(self):
        # Return a list of tuples (dbid, value) for all batters in year
        return []

    def pitcher_values(self):
        # Return a list of tuples (dbid, value) for all batters in year
        return []
    
##################################
## Linear valuation of players  ##
##################################    
        
class LinearValues(Valuation):
    # Player value is the normalized (within year) sum of his stats, adjusted to vorp
    # LinearValues(DB,year)
    #   - db: connected lahman db instance
    #   - year: year to compute values for
    def __init__(self,db,year):

        #need better normalization here!
        
        dat = db.batters(year,year)
        scorecats = [x[1][0:6] for x in dat]
        #scorecats = OBP, SLG, R, HR, RBI, SB
        normed,junk = normalize_stats(scorecats)
        scores = [ sum(x) for x in normed]
        self._bvals = [ (dat[ii][0][0], scores[ii]) for ii in range(len(dat))]

        dat = db.pitchers(year,year) #CHANGE NORMALIZATION FOR ERA AND WHIP
        scorecats = [list(x[1][0:3]) + [-1.0*x[1][3],-1.0*x[1][4], x[1][5]] for x in dat]
        #scorecats = W, SV, SO, -ERA, -WHIP, QS
        normed,junk = normalize_stats(scorecats)
        scores = [ sum(x) for x in normed]
        self._pvals = [ (dat[ii][0][0], scores[ii]) for ii in range(len(dat))]

    def batter_values(self):
        return self._bvals

    def pitcher_values(self):
        return self._pvals
        
        
#####################
## Tools for valuing players

def normalize_stats(stats):
    #determine a single value from a list of stats for all players
    # vals = normalize_stats(stats)
    # vals,norm = normalize_stats(stats)
    # each row of stats is the collection of statistics (larger better) for the players
    # the stats are normalized to the params.normPct percentile and summed for each player to get value
    # second return is normalizing values
    ncol = len(stats[0])
    norm = numpy.percentile(stats,params.normPct,axis=0)
    vals = [ [1.0*x[i] / abs(norm[i]) for i in range(0,ncol)] for x in stats]
    return vals,norm

def abs_to_vorp(absval, k, direct=False):
    #convert "absolute" player values to "value over replacement player"
    #vorp = abs_to_vorp(absval,k)
    # - (k+1)st best player is replacement player
    #vorp = abs_to_vorp(absval,k,direct=True)
    # - k is the absval score of the replacement player

    if direct:
        repval=k
    else:
        k = min(k,len(absval))
        srt = list(absval)
        srt.sort()
        repval = srt[-k]
        
    vorp = [x-repval for x in absval]
    return vorp

def to_samolians(vals, nPlayers):
    #Standardize values to samolians according to team budgets and number of players drafted
    #sams = to_samolians(vals, nPlayers)
    # vals - array of player values
    # nPlayers - number of these players on each team
    # sams - values in samolians

    cf = 1.0 * params.teamBudget * params.numTeams #Total amount of samolians
    cf *= nPlayers / (params.teamSize) #times fraction of total for these players
    cf /= sum(numpy.sort(vals)[-(nPlayers*params.numTeams):]) #divided by sum of values

    return [x*cf for x in vals]

