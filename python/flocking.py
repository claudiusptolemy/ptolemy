# flocking.py
# This file is part of the Ptolemy Layer for Google Earth project.
# It implements a method to compute unknown coordinates from known
# modern coordinates for locations given in Ptolemy. It is currently
# focused on book 7 (India region), but can and will be extended
# to other regions. 

import os
import sys

import numpy as np
from sklearn.neighbors import NearestNeighbors
from numpy import linalg

class Flocking(object):

    def __init__(self):
        self.k = 3

    def fit(self, X, y):
        # find the centers of both sets and compute the offset
        self.lat_off = X.ix[:,0].mean() - y.ix[:,0].mean()
        self.lon_off = X.ix[:,1].mean() - y.ix[:,1].mean()

        # move the ptol set so its over the other set
        self.move = np.zeros((len(X),2))
        self.move[:,0] = X.ix[:,0] - self.lat_off
        self.move[:,1] = X.ix[:,1] - self.lon_off

        # computer the vectors from the known ptols to their moderns
        self.vec = np.zeros((len(X),2))
        self.vec[:,0] = y.ix[:,0] - self.move[:,0]
        self.vec[:,1] = y.ix[:,1] - self.move[:,1]

        self.neighbors = NearestNeighbors(n_neighbors=self.k).fit(X)

    def predict(self, X):
        """Compute unknown modern coordinates from known ones using the
        given triangulation."""
        y = np.zeros((len(X),2))

        # for each unknown, find the knn knowns
        distances, indices = self.neighbors.kneighbors(X)

        # move the ptol set so its over the other set
        move = np.zeros((len(X),2))
        move[:,0] = X.ix[:,0] - self.lat_off
        move[:,1] = X.ix[:,1] - self.lon_off

        # compute the average vector for those knowns and use that as the
        # vector for the unknown apply that vector to the unknown and use
        # that as the prediction possibly: adjust the weights to be
        # quadratic on the dist to the neighbor
        _, k = distances.shape
        for i in range(len(X)):
            sum_dist = distances[i,:].sum()
            weights = (sum_dist - distances[i,:]) / ((k-1) * sum_dist)
            for j in range(2):
                vec = sum(self.vec[indices[i,:],j] * weights)
                y[i,j] = move[i,j] + vec

        return y
