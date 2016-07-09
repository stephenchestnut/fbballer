import params as p
import numpy as np
import loaddata

#####################
## Tools for valuing players

def stats_to_vals(stats):
    #determine a single value from a list of stats for each player
    # vals = stats_to_vals(stats)
    # each row of stats is the collection of statistics (larger better) for the players
    # the stats are normalized to the params.normPct percentile and summed for each player to get value
    norm = np.percentile(stats,p.normPct,axis=0)
    vals = [sum([1.0*x[i] / norm[i] for i in range(0,6)]) for x in stats]
    return vals

def abs_to_vorp(absval, k):
    #convert "absolute" player values to "value over replacement player"
    #vorp = abs_to_vorp(absval,k)
    #replacement player is taken to be the (k+1)th by value

    abscopy = list(absval)
    abscopy.sort() #sorted least to highest valuable
    if (k+1) > len(absval):
        rpval = 0
    else:
        rpval = abscopy[-(k+1)]

    vorp = [x-rpval for x in absval]
    return vorp

def to_samolians(vals, nPlayers):
    #Standardize values to samolians according to team budgets and number of players drafted
    #sams = to_samolians(vals, nPlayers)
    # vals - array of player values
    # nPlayers - number of these players on each team
    # sams - values in samolians

    cf = 1.0 * p.teamBudget * p.numTeams *nPlayers / (p.teamSize * sum(np.sort(vals)[-(nPlayers*p.numTeams):]))
    return [x*cf for x in vals]

def batter_value_fun():
    #fit a linear valuation function to the batters data
    #f = batter_value_fun()
    #f:(batter s,t,a,t,s)->values
    
    return value___linreg(loaddata.batters(),rcond=0.05)

def pitcher_value_fun():
    #fit a linear value function to the pitching data
    #f = pitching_value_fun()
    #f:(pitching s,t,a,t,s)->values
    
    return value___linreg(loaddata.pitchers(),rcond=0.05)

########################
### Helper functions ###
########################
def value___linreg(data,rcond=-1):
    #Fit a linear function to the batters or pitchers data,
    #drop singular values smaller than rcond*(spectral norm)
    #f = draftvalues___linreg(data)
    #f = draftvalues___linreg(data,rcond=0.01)
    xy = list(zip(*[(x[1][1:], x[1][0]) for x in data]))
    coeff = np.linalg.lstsq(xy[0], xy[1],rcond)
    def pricehim(x):
        return sum([coeff[0][i] * x[1][i+1] for i in range(0,len(coeff))])
    return pricehim
