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

def derive_unknown_modern_coords(known, unknown):
    """Compute unknown modern coordinates from known ones using the
    given triangulation."""

    k = 3

    X = known.loc[:, XCOLS]
    Y = unknown.loc[:, XCOLS]

    # find the centers of both sets and compute the offset
    lat_off = known.ptol_lat.mean() - known.modern_lat.mean()
    lon_off = known.ptol_lon.mean() - known.modern_lon.mean()

    # move the ptol set so its over the other set
    known.ix[:, 'move_lat'] = known.ptol_lat - lat_off
    known.ix[:, 'move_lon'] = known.ptol_lon - lon_off
    unknown.ix[:, 'move_lat'] = unknown.ptol_lat - lat_off
    unknown.ix[:, 'move_lon'] = unknown.ptol_lon - lon_off

    # computer the vectors from the known ptols to their moderns
    known.ix[:, 'vec_lat'] = known.modern_lat - known.move_lat
    known.ix[:, 'vec_lon'] = known.modern_lon - known.move_lon

    # for each unknown, find the knn knowns
    neighbors = NearestNeighbors(n_neighbors=k).fit(X)
    distances, indices = neighbors.kneighbors(Y)

    # computer the average vector for those knowns and use that as the
    # vector for the unknown apply that vector to the unknown and use
    # that as the prediction possibly: adjust the weights to be
    # quadratic on the dist to the neighbor
    for i in range(len(unknown)):
        sum_dist = distances[i,:].sum()
        weights = distances[i,:] / sum_dist
        vec_lat = sum(known.ix[indices[i,:], 'vec_lat'] * weights)
        vec_lon = sum(known.ix[indices[i,:], 'vec_lon'] * weights)
        unknown.ix[i, 'modern_lat'] = unknown.ix[i, 'move_lat'] + vec_lat
        unknown.ix[i, 'modern_lon'] = unknown.ix[i, 'move_lon'] + vec_lon

def main(filename):
    places = common.read_places()
    known, unknown = common.split_places(places)
    derive_unknown_modern_coords(known, unknown)
    common.write_kml_file(filename, None, known, unknown)
    common.write_csv_file(filename[0:-4]+'.csv', known, unknown)


if __name__ == '__main__':
    filename = sys.argv[1]
    main(filename)
