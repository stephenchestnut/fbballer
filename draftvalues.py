import numpy as np
import loaddata
import params as p

#####################
# Price 2015 players for 2016 draft
# (B, P) = NL2016Draft()
#
def NL2016Draft():

    B = nl_batter_vorp()
    P = nl_pitcher_vorp()
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

def nl_batter_vorp():
    #Compute NL 2015 batter vorp in samolians
    # B = nl_batter_vorp():
    # where rows of B are first name,last name,pos,vorp,id,s,t,a,t,s

    ##Load player performance data and compute values
    batval = batter_value_fun()
    B = loaddata.NLBatters2015()
    names = loaddata.NLNames2015()

    Bval = [batval(x) for x in B]
    nBatters=int(np.ceil(p.teamSize/2.0))
    Bvorp = abs_to_vorp(Bval, p.numTeams * nBatters)
    bcf = 1.0 * p.teamBudget * p.numTeams *nBatters / (p.teamSize * sum(np.sort(Bvorp)[-(nBatters*p.numTeams):]))

    #convert to samolians
    Bvorp = [x*bcf for x in Bvorp]

    B = list(zip(Bvorp,B))

    B = [names[x[1][0][0]] + (x[0], x[1][0][0]) + x[1][1][1:] for x in B]
    #first,last,pos,price,id,s,t,a,t,s

    return B

def nl_pitcher_vorp():
    #Compute NL 2015 pitcher vorp in samolians
    # P = nl_pitcher_vorp():
    # where rows of P are first name,last name,pos,vorp,id,s,t,a,t,s

    ##Load player performance data and compute values
    pitval = pitcher_value_fun()
    P = loaddata.NLPitchers2015()
    names = loaddata.NLNames2015()

    Pval = [pitval(x) for x in P]
    nPitchers=int(np.floor(p.teamSize/2.0))
    Pvorp = abs_to_vorp(Pval, p.numTeams * nPitchers)

    #batter and pitcher conversion factors (assuming equal spending on both)
    pcf = 1.0 * p.teamBudget * p.numTeams *nPitchers / (p.teamSize * sum(np.sort(Pvorp)[-(nPitchers*p.numTeams):]))
    #convert to samolians
    Pvorp = [x*pcf for x in Pvorp]

    P = list(zip(Pvorp,P))

    P = [names[x[1][0][0]] + (x[0], x[1][0][0]) + x[1][1][1:] for x in P]
    #first,last,pos,price,id,s,t,a,t,s

    return P
    


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
