# regression.py: Predict modern coordinates for places
# described by Ptolemy using linear regression against
# the places that have been suggested by other means.

import os
import sys
import csv
import random
import logging

import simplekml
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

import sgdb
import geocode
import common

XCOLS = ['ptol_lat','ptol_lon']
YCOLS = ['modern_lat','modern_lon']
NF = range(len(YCOLS))

class Regression(object):

    def __init__(self):
        self.m = [LinearRegression() for i in NF]

    def fit(self, X, y):
        for i in NF:
            self.m[i].fit(X, y.ix[:,i])
        
    def predict(self, X):
        y = np.zeros((len(X),2))
        for i in NF:
            y[:,i] = self.m[i].predict(X)
        return y

def main(filename):
    places = common.read_places()
    known, unknown = common.split_places(places)
    knownX = known.loc[:, XCOLS]
    knownY = known.loc[:, YCOLS]
    model = Regression()
    model.fit(knownX, knownY)
    unknownX = unknown.loc[:, XCOLS]
    unknownY = model.predict(unknownX)
    unknown.loc[:,YCOLS] = unknownY
    common.write_kml_file(filename, None, known, unknown)
    common.write_csv_file(filename[0:-4]+'.csv', known, unknown)

if __name__ == '__main__':
    filename = sys.argv[1]
    main(filename)
