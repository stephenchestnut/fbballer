# Predict valuations based on observed value in previous years

import numpy
import value
import loaddata

class Forecaster(object):
    #Base class for predicting future value based on past performance
    def __init__(self,styear,enyear,val):
        # use styear until enyear for training data, predictions for enyear+1
        # val is instance of Valuation gives scores to predict
        self.styear = styear
        self.enyear = enyear
        return

    def predict(self,dbids):
        # predict valuation of players in list dbids in year self.enyear+1
        return 0.0

class LinRegForecaster(Forecaster):

    def __init__(self,db,styear,enyear,ValClass):
        # LinRegForcaster(db,styear,enyear,ValClass)
        #  db - connected instance of Lahman DB
        #  styear - 1st year to draw training data (raw data)
        #  enyear - last year to draw traning values (computed values)
        #  ValClass - class of valuation type to use e.g. value.LinearValues
        if styear>enyear:
            print("you are a doofus")

        if styear==enyear: #only 1 year of data, predict everyone is same as last year
            v = ValClass(db,styear)
        else:
            v = ValClass(db,styear+1)

        bvals = dict(v.batter_values())
        pvals = dict(v.pitcher_values())
        #x = [bvals[k] for k in bvals]
        #x.sort()
        #print(x)
        bdatyr = db.batters(styear,styear)
        pdatyr = db.pitchers(styear,styear)
        bdat = [(lx, (bvals[lx[0]],)+rx) for (lx,rx) in bdatyr if lx[0] in bvals] #add values to the data
        pdat = [(lx, (pvals[lx[0]],)+rx) for (lx,rx) in pdatyr if lx[0] in pvals] #add values to the data
        for yr in range(styear+2,enyear):
            v = ValClass(db,yr)
            bvals = dict(v.batter_values())
            pvals = dict(v.pitcher_values())
            bdatyr = db.batters(yr-1,yr-1)
            pdatyr = db.pitchers(yr-1,yr-1)
            bdat += [(lx, (bvals[lx[0]],)+rx) for (lx,rx) in bdatyr if lx[0] in bvals] #add values to the data
            pdat += [(lx, (pvals[lx[0]],)+rx) for (lx,rx) in pdatyr if lx[0] in pvals] #add values to the data

        self.bvalfcn = self._linreg(bdat,rcond=0.01) #f:(batting s,t,a,t,s)->values
        self.pvalfcn = self._linreg(pdat,rcond=0.01) #f:(pitching s,t,a,t,s)->values
        
        return

    def predict(self,bdat,pdat):
        bpred = []
        ppred = []
        for ((dbid,yr),stats) in bdat:
            bpred += [self.bvalfcn(stats)]
        for ((dbid,yr),stats) in pdat:
            ppred += [self.pvalfcn(stats)]

        return bpred,ppred
    
    def _linreg(self,data,rcond=-1):
        # Fit a linear function to the batters or pitchers data,
        # drop singular values smaller than rcond*(spectral norm)
        #    f = linreg(data)
        #    f = linreg(data,rcond=0.01)

        xy = list(zip(*[(x[1][1:], x[1][0]) for x in data]))
        xy[0],nrmlz = value.normalize_stats(xy[0])
        coeff,*junk = numpy.linalg.lstsq(xy[0], xy[1],rcond)
        def valueplayer(x):
            return sum([coeff[i] * x[i] / nrmlz[i] for i in range(0,len(coeff))])
        return valueplayer
