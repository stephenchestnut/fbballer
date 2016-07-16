import params
import numpy
import loaddata

########################################
## Class for building valuation tools ##
########################################

class Valuation(object):
    
    def __init__(self):
        return
    
    def value_batters(self, batters):
        # Compute the value of a list of batters
        return [0.0]*len(players)

    def value_pitchers(self, pitchers):
        # Compute the value of a list of batters
        return [0.0]*len(players)

#####################################
## Valuations by linear regression ##
#####################################
    
class LinRegValuation(Valuation):
    # Value players by linear regression
    def __init__(self):
        db = loaddata.LahmanDB()
        db.connect()
        
        self.bvalfcn = self._linreg(db.batters(),rcond=0.05) #f:(batter s,t,a,t,s)->values
        self.pvalfcn = self._linreg(db.pitchers(),rcond=0.05) #f:(pitching s,t,a,t,s)->values

        db.disconnect
        
        return
        
    def _linreg(self,data,rcond=-1):
        # Fit a linear function to the batters or pitchers data,
        # drop singular values smaller than rcond*(spectral norm)
        #    f = linreg(data)
        #    f = linreg(data,rcond=0.01)
        
        xy = list(zip(*[(x[1][1:], x[1][0]) for x in data]))
        coeff = numpy.linalg.lstsq(xy[0], xy[1],rcond)
        def pricehim(x):
            return sum([coeff[0][i] * x[1][i+1] for i in range(0,len(coeff))])
        return pricehim
        
#####################
## Tools for valuing players

def normalize_stats(stats):
    #determine a single value from a list of stats for all players
    # vals = stats_to_vals(stats)
    # each row of stats is the collection of statistics (larger better) for the players
    # the stats are normalized to the params.normPct percentile and summed for each player to get value
    norm = numpy.percentile(stats,params.normPct,axis=0)
    vals = [sum([1.0*x[i] / norm[i] for i in range(0,6)]) for x in stats]
    return vals

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

