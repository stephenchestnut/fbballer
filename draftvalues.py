import numpy as np
import loaddata
import params as p

#####################
# Price 2015 players for 2016 draft
# (B, P) = NL2016Draft()
#
def NL2016Draft():

    ##Load player performance data and compute values
    batval = batter_value_fun()
    pitval = pitcher_value_fun()

    B = loaddata.NLBatters2015()
    P = loaddata.NLPitchers2015()
    names = loaddata.NLNames2015()

    Bval = [batval(x) for x in B]
    Pval = [pitval(x) for x in P]

    ##Convert value to samolians by assuming top 11*9 batters and top 10*9 pitchers are drafted
    nBatters=int(np.ceil(p.teamSize/2.0))
    nPitchers=int(np.floor(p.teamSize/2.0))
    #batter and pitcher conversion factors (assuming equal spending on both)
    bcf = 1.0 * p.teamBudget * p.numTeams *nBatters / (p.teamSize * sum(np.sort(Bval)[-(nBatters*p.numTeams):]))
    pcf = 1.0 * p.teamBudget * p.numTeams *nPitchers / (p.teamSize * sum(np.sort(Pval)[-(nPitchers*p.numTeams):]))
    #convert to samolians
    Bval = [x*bcf for x in Bval]
    Pval = [x*pcf for x in Pval]

    B = list(zip(Bval,B))
    P = list(zip(Pval,P))

    B = [names[x[1][0][0]] + (x[0], x[1][0][0]) + x[1][1][1:] for x in B]
    #first,last,pos,price,id,s,t,a,t,s
    P = [names[x[1][0][0]] + (x[0], x[1][0][0]) + x[1][1][1:] for x in P]
    #first,last,pos,price,id,s,t,a,t,s

    return (B,P)
    
def batter_value_fun():
    #fit a linear valuation function to the batters data
    #f = batter_value_fun()
    #f:(batter s,t,a,t,s)->values
    
    return draftvalues___linreg(loaddata.batters(),rcond=0.05)

def pitcher_value_fun():
    #fit a linear value function to the pitching data
    #f = pitching_value_fun()
    #f:(pitching s,t,a,t,s)->values
    
    return draftvalues___linreg(loaddata.pitchers(),rcond=0.05)

########################
### Helper functions ###
########################
def draftvalues___linreg(data,rcond=-1):
    #Fit a linear function to the batters or pitchers data,
    #drop singular values smaller than rcond*(spectral norm)
    #f = draftvalues___linreg(data)
    #f = draftvalues___linreg(data,rcond=0.01)
    xy = list(zip(*[(x[1][1:], x[1][0]) for x in data]))
    coeff = np.linalg.lstsq(xy[0], xy[1],rcond)
    def pricehim(x):
        return sum([coeff[0][i] * x[1][i+1] for i in range(0,len(coeff))])
    return pricehim
