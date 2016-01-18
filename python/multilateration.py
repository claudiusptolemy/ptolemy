# multilateration.py
# This file is part of the Ptolemy Layer for Google Earth project.
# It implements a method to compute unknown coordinates from known
# modern coordinates for locations given in Ptolemy. It is currently
# focused on book 7 (India region), but can and will be extended
# to other regions. 
# 
# This particular program works by using multilateration of the 
# nearest known neighbors of each unknown coordinate.

from math import *

import numpy as np
from sklearn.neighbors import NearestNeighbors

from pysatsnip import geodetic2ecef, ecef2geodetic


# adapted from an algorithm listed here:
# http://stackoverflow.com/questions/8318113/multilateration-of-gps-coordinates
def multilaterate(P, dists):
    r = 6378.137  # Earth radius in kilometers
    a = []
    for m in range(0, len(P)):
        x = P[m][0]
        y = P[m][1]
        z = P[m][2]
        am = -2*x
        bm = -2*y
        cm = -2*z
        dm = r*r + (pow(x, 2) +
                    pow(y, 2) +
                    pow(z, 2)) - pow(dists[m], 2)
        a += [[am, bm, cm, dm]]
    # Solve using SVD
    a = np.array(a)
    (_, _, v) = np.linalg.svd(a)
    # Get the minimizer
    w = v[3, :]
    w /= w[3]  # Resulting position in ECEF
    return w[:3]


def euclidean_distance(a, b):
    return sqrt(sum(pow(a[i] - b[i], 2) for i in range(len(a))))


class Multilateration(object):

    def __init__(self):
        self.trainX = None
        self.trainY = None
        self.neighbors = None

    def fit(self, x, y):
        self.trainX = x
        self.trainY = y
        self.neighbors = NearestNeighbors(n_neighbors=3).fit(x)

    def predict(self, x):
        """Compute unknown modern coordinates from known ones using the
        given triangulation."""
        distances, indices = self.neighbors.kneighbors(x)
        y = np.zeros((len(x), 2))
        for i in range(len(x)):
            ai, bi, ci = tuple(indices[i, j] for j in range(3))
            ax = self.trainX.iloc[ai].values
            bx = self.trainX.iloc[bi].values
            cx = self.trainX.iloc[ci].values
            tx = x.iloc[i].values
            ay = self.trainY.iloc[ai].values
            by = self.trainY.iloc[bi].values
            cy = self.trainY.iloc[ci].values
            p = [geodetic2ecef(c[0], c[1], 0) for c in [ax, bx, cx]]
            txecef = geodetic2ecef(tx[0], tx[1], 0)
            pd = [euclidean_distance(txecef, c) for c in p]
            q = [geodetic2ecef(c[0], c[1], 0) for c in [ay, by, cy]]
            tyecef = multilaterate(q, pd)
            y[i, :] = ecef2geodetic(tyecef[0], tyecef[1], tyecef[2])
        return y
