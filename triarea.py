# triangulate.py
# This file is part of the Ptolemy Layer for Google Earth project.
# It implements a method to compute unknown coordinates from known
# modern coordinates for locations given in Ptolemy. It is currently
# focused on book 7 (India region), but can and will be extended
# to other regions.

import os
import sys

import numpy as np
import pandas as pd
from scipy.spatial import Delaunay
from scipy.optimize import minimize

from triangulate import weights

def objective(x, mp, ap, bp, cp, am, bm, cm):
    w1 = weights(ap, bp, cp, mp)
    w2 = weights(am, bm, cm, x)
    return sum(w1[i]*w2[i] for i in range(len(w1)))

def solver(x0, mp, ap, bp, cp, am, bm, cm):
    try:
        res = minimize(objective, x0, (mp,ap,bp,cp,am,bm,cm),
                       'CG', False, tol=0.001)
        return tuple(res.x)
    except ValueError:
        return (0.0, 0.0)

class Triarea(object):

    def fit(self, X, y):
        self.trainX = X
        self.trainY = y
        self.tri = Delaunay(X, furthest_site=False)

    def predict(self, X):
        """Compute unknown modern coordinates from known ones using the
        given triangulation."""
        simps = self.tri.find_simplex(X)
        y = np.zeros((len(simps),2))
        for i in range(len(simps)):
            s = simps[i]
            simp = self.tri.simplices[s]
            if s > -1:
                p = X.iloc[i,:]
                ap, bp, cp = tuple(tuple(self.trainX.iloc[j]) for j in simp)
                am, bm, cm = tuple(tuple(self.trainY.iloc[j]) for j in simp)
                mp = tuple(p)
                x0 = tuple((am[i]+bm[i]+cm[i])/3.0 for i in range(2))
                y[i,:] = solver(x0, mp, ap, bp, cp, am, bm, cm)
        return y
