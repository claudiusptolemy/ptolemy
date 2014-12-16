# flocking.py
# This file is part of the Ptolemy Layer for Google Earth project.
# It implements a method to compute unknown coordinates from known
# modern coordinates for locations given in Ptolemy. It is currently
# focused on book 7 (India region), but can and will be extended
# to other regions. 

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

XCOLS = ['ptol_lat','ptol_lon']
YCOLS = ['modern_lat','modern_lon']

class FlockingModel(object):

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

        # computer the average vector for those knowns and use that as the
        # vector for the unknown apply that vector to the unknown and use
        # that as the prediction possibly: adjust the weights to be
        # quadratic on the dist to the neighbor
        for i in range(len(X)):
            sum_dist = distances[i,:].sum()
            weights = distances[i,:] / sum_dist
            vec_lat = sum(self.vec[indices[i,:],0] * weights)
            vec_lon = sum(self.vec[indices[i,:],1] * weights)
            y[i,0] = move[i,0] + vec_lat
            y[i,1] = move[i,1] + vec_lon

        return y

def main(filename):
    places = common.read_places()
    known, unknown = common.split_places(places)
    knownX = known.loc[:, XCOLS]
    knownY = known.loc[:, YCOLS]
    model = FlockingModel()
    model.fit(knownX, knownY)
    unknownX = unknown.loc[:, XCOLS]
    unknownY = model.predict(unknownX)
    unknown.loc[:,YCOLS] = unknownY
    common.write_kml_file(filename, None, known, unknown)
    common.write_csv_file(filename[0:-4]+'.csv', known, unknown)

if __name__ == '__main__':
    filename = sys.argv[1]
    main(filename)
