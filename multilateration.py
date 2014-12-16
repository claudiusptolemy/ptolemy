# multilateration.py
# This file is part of the Ptolemy Layer for Google Earth project.
# It implements a method to compute unknown coordinates from known
# modern coordinates for locations given in Ptolemy. It is currently
# focused on book 7 (India region), but can and will be extended
# to other regions. 
# 
# This particular program works by using multilateration of the 
# nearest known neighbors of each unknown coordinate.

import os
import sys
import math
import logging

import simplekml
import numpy as np
import pandas as pd
from geopy.distance import vincenty
from scipy.spatial import Delaunay
from sklearn.neighbors import NearestNeighbors
from numpy import linalg

import sgdb
import geocode
import common

from pysatsnip import geodetic2ecef, ecef2geodetic

XCOLS = ['ptol_lat','ptol_lon']
YCOLS = ['modern_lat','modern_lon']

# adapted from an algorithm listed here:
# http://stackoverflow.com/questions/8318113/multilateration-of-gps-coordinates
def multilaterate(P, dists):
    R = 6378.137 # Earth radius in kilometers
    A = []
    for m in range(0,len(P)):
        x = P[m][0]
        y = P[m][1]
        z = P[m][2]
        Am = -2*x
        Bm = -2*y
        Cm = -2*z
        Dm = R*R + (math.pow(x,2) +
                    math.pow(y,2) +
                    math.pow(z,2)) - math.pow(dists[m],2)
        A += [[Am,Bm,Cm,Dm]]
    # Solve using SVD
    A = np.array(A)
    (_,_,v) = np.linalg.svd(A)
    # Get the minimizer
    w = v[3,:]
    w /= w[3] # Resulting position in ECEF
    return w[:3]

def euclidean_distance(a, b):
    return math.sqrt(sum(math.pow(a[i] - b[i], 2) for i in range(len(a))))

class MultilaterationModel(object):

    def __init__(self):
        pass

    def fit(self, X, y):
        self.trainX = X
        self.trainY = y
        self.neighbors = NearestNeighbors(n_neighbors=3).fit(X)

    def predict(self, X):
        """Compute unknown modern coordinates from known ones using the
        given triangulation."""
        distances, indices = self.neighbors.kneighbors(X)
        y = np.zeros((len(X),2))
        print len(X)
        for i in range(len(X)):
            print '-' * 60
            ai, bi, ci = tuple(indices[i,j] for j in range(3))
            ax = self.trainX.iloc[ai].values
            bx = self.trainX.iloc[bi].values
            cx = self.trainX.iloc[ci].values
            tx = X.iloc[i].values
            ay = self.trainY.iloc[ai].values
            by = self.trainY.iloc[bi].values
            cy = self.trainY.iloc[ci].values
            print [(c[0],c[1]) for c in [ax,bx,cx]]
            P = [geodetic2ecef(c[0],c[1],0) for c in [ax,bx,cx]]
            txecef = geodetic2ecef(tx[0],tx[1],0)
            print P
            Pd = [euclidean_distance(txecef, c) for c in P]
            print Pd
            ntxecef = multilaterate(P, Pd)
            ntx = ecef2geodetic(ntxecef[0], ntxecef[1], ntxecef[2])
            print ntx
            print (tx[0],tx[1])
            Q = [geodetic2ecef(c[0],c[1],0) for c in [ay,by,cy]]
            tyecef = multilaterate(Q, Pd)
            y[i,:] = ecef2geodetic(tyecef[0], tyecef[1], tyecef[2])
            print y[i,:]
        return y

def main(filename):
    places = common.read_places()
    known, unknown = common.split_places(places)
    knownX = known.loc[:, XCOLS]
    knownY = known.loc[:, YCOLS]
    model = MultilaterationModel()
    model.fit(knownX, knownY)
    unknownX = unknown.loc[:, XCOLS]
    unknownY = model.predict(unknownX)
    unknown.loc[:,YCOLS] = unknownY
    common.write_kml_file(filename, None, known, unknown)
    common.write_csv_file(filename[0:-4]+'.csv', known, unknown)

if __name__ == '__main__':
    filename = sys.argv[1]
    main(filename)
