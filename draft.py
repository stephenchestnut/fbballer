import numpy as np
import loaddata
import params as p
import value
import forecast

#Load data and compute the valuation function
#lrv = forcast.LinRegValuation()

#####################
# Price 2015 players for 2016 draft
# (B, P) = NL2016Draft()
#
def NL2016Draft():

    db = loaddata.LahmanDB()
    nl2015db = loaddata.LahmanNL2015()
    db.connect()
    nl2015db.connect()

    lr = forecast.LinRegForecaster(db, p.minYear, p.maxYear, value.LinearValues)
    #B = nl_batter_vorp2016()
    #P = nl_pitcher_vorp2016()

    batstats = nl2015db.NLBatters2015()
    pitstats = nl2015db.NLPitchers2015()
    names = nl2015db.NLNames2015()
    #Compute values
    batval,pitval = lr.predict( batstats, pitstats )

    #Vorp the values and convert to samolians
    batval = value.abs_to_vorp(batval,p.numTeams * int(np.ceil(p.teamSize / 2)))
    batval = value.to_samolians(batval, int(np.ceil(p.teamSize / 2)))
    pitval = value.abs_to_vorp(pitval,p.numTeams * int(np.floor(p.teamSize / 2)))
    pitval = value.to_samolians(pitval, int(np.floor(p.teamSize / 2)))
    
    B=[]
    for ii in range(len(batstats)):
        B+=[ list(names[batstats[ii][0][0]]) + [batstats[ii][0][1]] + [batval[ii]] + list(batstats[ii][1]) ]
    P=[]
    for ii in range(len(pitstats)):
        P+=[ list(names[pitstats[ii][0][0]]) + [pitstats[ii][0][1]] + [pitval[ii]] + list(pitstats[ii][1]) ]

    db.disconnect()
    nl2015db.disconnect()
    
    return (B,P)
    
def nl_batter_vorp2016():
    #Compute NL 2015 batter vorp in samolians
    # B = nl_batter_vorp2015():
    # where rows of B are first name,last name,pos,vorp,id,s,t,a,t,s

    ##Load player performance data and compute values
    db2015 = loaddata.LahmanNL2015()
    db2015.connect()
    B = db2015.NLBatters2015()
    names = db2015.NLNames2015()
    db2015.disconnect()

    nBatters=int(np.ceil(p.teamSize/2.0)) #expected number of batters on a team

    Bval = [lrv.bvalfcn(x) for x in B]
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
    db2015=loaddata.LahmanNL2015()
    db2015.connect()
    P = db2015.NLPitchers2015()
    names = db2015.NLNames2015()
    db2015.disconnect()
    
    nPitchers=int(np.floor(p.teamSize/2.0)) # expected number of pitcher on a team

    Pval = [lrv.pvalfcn(x) for x in P]
    Pval = value.abs_to_vorp(Pval, p.numTeams * nPitchers)
    Pval = value.to_samolians(Pval, nPitchers) 

    P = list(zip(Pval,P))

    P = [names[x[1][0][0]] + (x[0], x[1][0][0]) + x[1][1][1:] for x in P]
    #first,last,pos,price,id,s,t,a,t,s

    return P


