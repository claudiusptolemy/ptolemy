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
from math import *

import simplekml
import numpy as np
from sklearn.neighbors import NearestNeighbors
from numpy import linalg

from pysatsnip import geodetic2ecef, ecef2geodetic

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
        Dm = R*R + (pow(x,2) +
                    pow(y,2) +
                    pow(z,2)) - pow(dists[m],2)
        A += [[Am,Bm,Cm,Dm]]
    # Solve using SVD
    A = np.array(A)
    (_,_,v) = np.linalg.svd(A)
    # Get the minimizer
    w = v[3,:]
    w /= w[3] # Resulting position in ECEF
    return w[:3]

def euclidean_distance(a, b):
    return sqrt(sum(pow(a[i] - b[i], 2) for i in range(len(a))))

class Multilateration(object):

    def fit(self, X, y):
        self.trainX = X
        self.trainY = y
        self.neighbors = NearestNeighbors(n_neighbors=3).fit(X)

    def predict(self, X):
        """Compute unknown modern coordinates from known ones using the
        given triangulation."""
        distances, indices = self.neighbors.kneighbors(X)
        y = np.zeros((len(X),2))
        for i in range(len(X)):
            ai, bi, ci = tuple(indices[i,j] for j in range(3))
            ax = self.trainX.iloc[ai].values
            bx = self.trainX.iloc[bi].values
            cx = self.trainX.iloc[ci].values
            tx = X.iloc[i].values
            ay = self.trainY.iloc[ai].values
            by = self.trainY.iloc[bi].values
            cy = self.trainY.iloc[ci].values
            P = [geodetic2ecef(c[0],c[1],0) for c in [ax,bx,cx]]
            txecef = geodetic2ecef(tx[0],tx[1],0)
            Pd = [euclidean_distance(txecef, c) for c in P]
            ntxecef = multilaterate(P, Pd)
            ntx = ecef2geodetic(ntxecef[0], ntxecef[1], ntxecef[2])
            Q = [geodetic2ecef(c[0],c[1],0) for c in [ay,by,cy]]
            tyecef = multilaterate(Q, Pd)
            y[i,:] = ecef2geodetic(tyecef[0], tyecef[1], tyecef[2])
        return y
