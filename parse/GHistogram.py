#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 29 12:12:27 2019

@author: rchiechi
"""

from scipy.optimize import curve_fit
from scipy.stats import gmean,skew,skewtest,kurtosis,kurtosistest
import numpy as np

class GHistogram2d:

    
    def __init__(self, logger, distanceData, currentData):
        self.name = 'GD-histrogram parser'
        self.I = currentData
        self.D = distanceData
        self.logger = logger
        self.histogram = {'H':[[0],[0]], 'Dedges': [], 'Gedges':[]}
        self.fits = {}
        self.run()
        
    def run(self):
        self.logger.info("Starting %s", self.name)
        G = np.array(self.I)/0.1/0.0000775
        D = np.array(self.D)
        if G.any() < 0:
            self.logger.warn("Dataset contains negative G-values!")
        nbins = int(len(G)/100)
        if nbins > 5000:
            nbins = 5000
        print("nbins: %s" % nbins)
#        nbins = 5000
        if len(G) < 10:
            self.logger.warn("Histogram with only %d points.", len(G))
            nbins = 10
        try:

            H, Dedges, Gedges = np.histogram2d(D, G, bins=nbins)
            H = H.T  # Let each row list bins with common y range.
        except ValueError as msg:
            #TODO we can now split out the file name with the bad data in it!
            self.logger.warning("Encountered this error while constructing histogram: %s", str(msg), exc_info=False)
            H = np.array([[0.],[0.]])
            Dedges = [0.]
            Gedges = [0.]
            
        self.histogram = {'H':H, 'Dedges': Dedges, 'Gedges':Gedges}

        self.logger.info("%s run loop done", self.name)

            


class GHistogram:

    
    def __init__(self, logger, currentData):
        self.name = 'G-histrogram parser'
        self.I = currentData
        self.logger = logger
        self.histogram = {'freq':[0], 'bins':[0]}
        self.fits = {}
        self.run()
        
    def run(self):
        self.logger.info("Starting %s", self.name)
        G = np.array(self.I)/0.1/0.0000775
        if G.any() < 0:
            self.logger.warn("Dataset contains negative G-values!")
#        try:
#            Grange = (G.min(),G.max())
#        except ValueError as msg:
#            self.logger.error("Error ranging data for histogram: %s" % str(msg))
#            Grange = (0,0)
        nbins = int(len(G)/100)
        if nbins > 5000:
            nbins = 5000
        print("nbins: %s" % nbins)
#        nbins = 5000
        if len(G) < 10:
            self.logger.warn("Histogram with only %d points.", len(G))
            nbins = 10
        try:
            #TODO Why not offer density plots as an option?
#            freq, bins = np.histogram(G, range=Grange, bins=nbins, density=True)
            freq, bins = np.histogram(G, bins=nbins, density=True)

        except ValueError as msg:
            #TODO we can now split out the file name with the bad data in it!
            self.logger.warning("Encountered this error while constructing histogram: %s", str(msg), exc_info=False)
            bins=np.array([0.,0.,0.,0.])
            freq=np.array([0.,0.,0.,0.])
        
        if len(G):  
            Gm = signedgmean(G)
            Gs = abs(G.std())
        else:
            Gm,Gs = 0.0,0.0

        p0 = [1., Gm, Gs]
        bin_centers = (bins[:-1] + bins[1:])/2
        self.histogram['freq'] = freq
        self.histogram['bins'] = bin_centers
        coeff = p0
        covar = None
        hist_fit = np.array([x*0 for x in range(0, len(bin_centers))])
        try:
            coeff, covar = curve_fit(lorenz, bin_centers, freq, p0=p0, maxfev=1000)
            hist_fit = lorenz(bin_centers, *coeff)
            
#                coeff, covar = curve_fit(gauss, bin_centers, freq, p0=p0, maxfev=1000)
#                hist_fit = gauss(bin_centers, *coeff)
        except RuntimeError as msg:              
            self.logger.warning("Fit did not converge (%s)", str(msg), exc_info=False)
        except ValueError as msg:
            self.logger.warning("Skipping data with ridiculous numbers in it (%s)", str(msg), exc_info=False )
            #coeff=p0

        #hist_fit = np.array([x*0 for x in range(0, len(bin_centers))])
        
        #if covar != None:
        #    self.logger.debug('Covariance: %s ' % (np.sqrt(np.diag(covar))) )
#        if len(bins) > len(freq):
#            while len(bins) > len(freq):
#                bins = bins[:-1]
#        if len(freq) > len(bins):
#            while len(freq) > len(bins):
#                freq = freq[:-1]            
        skewstat, skewpval = skewtest(freq)
        kurtstat, kurtpval = kurtosistest(freq)
        self.fits = {"bins":bin_centers, "bin_edges":bins, "freq":freq, "mean":coeff[1], "std":coeff[2], \
                "var":coeff[2], "fit":hist_fit, "Gmean":Gm, "Gstd":Gs,\
                "skew":skew(freq), "kurtosis":kurtosis(freq), "skewstat":skewstat, "skewpval":skewpval,
                "kurtstat":kurtstat, "kurtpval":kurtpval}
        self.logger.info("%s run loop done", self.name)
#            self.alive.clear()
            

def signedgmean(Y):
    '''
    Return a geometric average with the
    same sign as the input data assuming
    all values have the same sign
    '''
    if len(Y[Y<0]): Ym = -1*gmean(abs(Y))
    else: Ym = gmean(abs(Y))
    return Ym
       
        
def gauss(x, *p):
    '''
    Return a gaussian function
    '''
    A, mu, sigma = p
    return A*np.exp(-(x-mu)**2/(2.*sigma**2))

def lorenz(x, *p):
    '''
    Return a lorenzian function
    '''
    A, mu, B = p
    return A/( (x-mu)**2 + B**2)