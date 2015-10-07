# triangulate.py
# This file is part of the Ptolemy Layer for Google Earth project.
# It implements a method to compute unknown coordinates from known
# modern coordinates for locations given in Ptolemy. It is currently
# focused on book 7 (India region), but can and will be extended
# to other regions.

import os
import sys
from math import *

import numpy as np
from scipy.spatial import Delaunay

def mgc_distance(a, b, gamma=0.95):
    """Return the modified greatest circle distance based on the radian
    latitude and longitude coordinates a and b in terms of radians, adjusted
    by gamma."""
    return 2.0 * asin(min(1, sqrt(sin(abs(a[0] - b[0])/2.0) ** 2 +
                                  cos(a[0]) * cos(b[0]) *
                                  sin((gamma*abs(a[1] - b[1]))/2.0) ** 2)))

def sphere_tri_area(x):
    """Compute the area of the triangle defined by the three radian
    latitude and longitude coordinate pairs given by x."""
    s = sum(x) / 2.0
    return 4.0 * atan(sqrt(tan(s / 2.0) *
                           tan((s - x[0]) / 2.0) *
                           tan((s - x[1]) / 2.0) *
                           tan((s - x[2]) / 2.0)))

def weights(a, b, c, m):
    """Compute the weights to use for the three latitude and longitude
    coordinate pairs for a, b, and c, to find the coordinate pair
    m. This can then be used to compute a new coordinate pair for m
    based on alternative coordinates for a, b, and c. """
    a, b, c, m = ((radians(lat), radians(lon)) for (lat, lon) in (a, b, c, m))
    ab, bc, ca = (mgc_distance(x,y) for (x,y) in ((a,b), (b,c), (c,a)))
    ma, mb, mc = (mgc_distance(x,y) for (x,y) in ((m,a), (m,b), (m,c)))
    ta, tb, tc = ((mb,mc,bc), (ma,mc,ca), (ma,mb,ab))
    sa, sb, sc = (sphere_tri_area(x) for x in (ta, tb, tc))
    ss = sa + sb + sc
    return tuple(s / ss for s in (sa, sb, sc))

def new_point(x, w):
    """Compute a new latitude and longitude coordinate pair by combining the
    three pairs in x according to the weights given in w."""
    return (sum(w[i] * x[i][0] for i in range(3)),
            sum(w[i] * x[i][1] for i in range(3)))

class Triangulate(object):

    def fit(self, X, y):
        self.trainX = X
        self.trainy = y
        self.tri = Delaunay(X, furthest_site=False)

    def predict(self, X):
        simps = self.tri.find_simplex(X)
        y = np.zeros((len(simps),2))
        for i in range(len(simps)):
            s = simps[i]
            simp = self.tri.simplices[s]
            if s > -1:
                p = X.iloc[i,:]
                ap, bp, cp = tuple(tuple(self.trainX.iloc[j]) for j in simp)
                am, bm, cm = tuple(tuple(self.trainy.iloc[j]) for j in simp)
                mp = tuple(p)
                w = weights(ap, bp, cp, mp)
                y[i,:] = new_point((am, bm, cm), w)
        return y
