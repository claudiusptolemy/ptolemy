# basis.py
# This file is part of the Ptolemy Layer for Google Earth project.
# It implements a method to compute unknown coordinates from known
# modern coordinates for locations given in Ptolemy. It is currently
# focused on book 7 (India region), but can and will be extended
# to other regions. 
# 
# This particular program works by viewing the nearest three known
# neighbors as a basis for each unknown, and then doing a change of
# basis to the modern coordinates for those three known places.

import numpy as np
from sklearn.neighbors import NearestNeighbors
from numpy import linalg

def change_basis(ax, bx, cx, tx, ay, by, cy):
    """Find the position ty based on basis formed by vectors ay, by and
    ay, cy, by finding its coordinates using tx on the basis formed by
    vectors ax, bx, and ax, cx."""
    px = ax - cx
    qx = bx - cx
    rx = tx - cx
    A = np.matrix(np.column_stack([px, qx]))
    rv = linalg.solve(A, rx)
    py = ay - cy
    qy = by - cy
    B = np.matrix(np.column_stack([py, qy]))
    ry = np.array((B * np.matrix(rv).transpose()).transpose())[0]
    ty = ry + cy
    return ty

class Basis(object):
    
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
            try:
                y[i,:] = change_basis(ax, bx, cx, tx, ay, by, cy)
            except linalg.LinAlgError as e:
                print 'warning:%s:%s' % (i,e)
        return y
