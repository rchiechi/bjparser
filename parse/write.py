#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  2 15:27:22 2019

@author: rchiechi
"""

import os
import csv


csv.register_dialect('GHist', delimiter='\t', quoting=csv.QUOTE_MINIMAL)



def Ghistwriter(logger, outdir, Ghist):
    # Ghist is a parse.GHistogram object
    
    if not os.path.exists(outdir):
        logger.info("%s does not exist, creating.", outdir)
        os.mkdir(outdir)
    fn = os.path.join(outdir, 'GHistogram.csv')
    with open(fn, 'w', newline='') as csvfile:    
        writer = csv.writer(csvfile, dialect='GHist')
        headers = ["G/G0", "Frequency"]
        writer.writerow(headers)
        for i in range(0, len(Ghist.histogram['bins'])):
            writer.writerow(["%0.16f"%Ghist.histogram['bins'][i],
                             "%0.4f"%Ghist.histogram['freq'][i]])

#            self.fits = {"bin_centers":bin_centers, "bins":bins, "freq":freq, "mean":coeff[1], "std":coeff[2], \
#                "var":coeff[2], "bins":bins, "fit":hist_fit, "Gmean":Gm, "Gstd":Gs,\
#                "skew":skew(freq), "kurtosis":kurtosis(freq), "skewstat":skewstat, "skewpval":skewpval,
#                "kurtstat":kurtstat, "kurtpval":kurtpval}
            
            