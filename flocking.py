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

    # computer the average vector for those knowns and use that as the vector for the unknown
    # apply that vector to the unknown and use that as the prediction
    # possibly: adjust the weights to be quadratic on the dist to the neighbor
    for i in range(len(unknown)):
        #vec_lat = known.ix[indices[i,:], 'vec_lat'].mean()
        #vec_lon = known.ix[indices[i,:], 'vec_lon'].mean()
        sum_dist = distances[i,:].sum()
        weights = distances[i,:] / sum_dist
        vec_lat = sum(known.ix[indices[i,:], 'vec_lat'] * weights)
        vec_lon = sum(known.ix[indices[i,:], 'vec_lon'] * weights)
        unknown.ix[i, 'modern_lat'] = unknown.ix[i, 'move_lat'] + vec_lat
        unknown.ix[i, 'modern_lon'] = unknown.ix[i, 'move_lon'] + vec_lon
        #ai, bi, ci = tuple(indices[i,j] for j in range(k))
        #unknown.ix[i, 'modern_lat'] = ty[0]
        #unknown.ix[i, 'modern_lon'] = ty[1]
        #append_debug_coords(unknown, i, ax, bx, cx, ay, by, cy)

def main(filename):
    places = common.read_places()
    known, unknown = common.split_places(places)
    #unknown = unknown.ix[range(5), :]
    derive_unknown_modern_coords(known, unknown)
    common.write_kml_file(filename, None, known, unknown)
    common.write_csv_file(filename[0:-4]+'.csv', known, unknown)


if __name__ == '__main__':
    filename = sys.argv[1]
    main(filename)
