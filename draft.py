import numpy as np
import loaddata
import params as p
import value

#####################
# Price 2015 players for 2016 draft
# (B, P) = NL2016Draft()
#
def NL2016Draft():

    B = nl_batter_vorp2016()
    P = nl_pitcher_vorp2016()
    return (B,P)
    
def nl_batter_vorp2016():
    #Compute NL 2015 batter vorp in samolians
    # B = nl_batter_vorp2015():
    # where rows of B are first name,last name,pos,vorp,id,s,t,a,t,s

    ##Load player performance data and compute values
    batval = value.batter_value_fun()
    B = loaddata.NLBatters2015()
    names = loaddata.NLNames2015()

    nBatters=int(np.ceil(p.teamSize/2.0)) #expected number of batters on a team

    Bval = [batval(x) for x in B]
    Bval = value.abs_to_vorp(Bval, p.numTeams * nBatters)
    Bval = value.to_samolians(Bval, nBatters)

    B = list(zip(Bval,B))

    B = [names[x[1][0][0]] + (x[0], x[1][0][0]) + x[1][1][1:] for x in B]
    #first,last,pos,price,id,s,t,a,t,s

    return B

def nl_pitcher_vorp2016():
    #Compute NL 2015 pitcher vorp in samolians
    # P = nl_pitcher_vorp2015():
    # where rows of P are first name,last name,pos,vorp,id,s,t,a,t,s

    ##Load player performance data and compute values
    pitval = value.pitcher_value_fun()
    P = loaddata.NLPitchers2015()
    names = loaddata.NLNames2015()

    nPitchers=int(np.floor(p.teamSize/2.0)) # expected number of pitcher on a team

    Pval = [pitval(x) for x in P]
    Pval = value.abs_to_vorp(Pval, p.numTeams * nPitchers)
    Pval = value.to_samolians(Pval, nPitchers) 

    P = list(zip(Pval,P))

    P = [names[x[1][0][0]] + (x[0], x[1][0][0]) + x[1][1][1:] for x in P]
    #first,last,pos,price,id,s,t,a,t,s

    return P


