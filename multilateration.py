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
    X = known.loc[:, XCOLS]
    Y = unknown.loc[:, XCOLS]
    neighbors = NearestNeighbors(n_neighbors=3).fit(X)
    distances, indices = neighbors.kneighbors(Y)
    print len(unknown)
    for i in range(len(unknown)):
        print '-' * 60
        ai, bi, ci = tuple(indices[i,j] for j in range(3))
        ax = known.ix[ai, XCOLS].values
        bx = known.ix[bi, XCOLS].values
        cx = known.ix[ci, XCOLS].values
        tx = unknown.ix[i, XCOLS].values
        ay = known.ix[ai, YCOLS].values
        by = known.ix[bi, YCOLS].values
        cy = known.ix[ci, YCOLS].values
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
        #Qdscale = [euclidean_distance(ax, bx) / euclidean_distance(ay, by),
        #           euclidean_distance(bx, cx) / euclidean_distance(by, cy),
        #           euclidean_distance(cx, ax) / euclidean_distance(cy, ay)]
        #print 'scale:', Qdscale
        tyecef = multilaterate(Q, Pd)
        ty = ecef2geodetic(tyecef[0], tyecef[1], tyecef[2])
        print ty
        unknown.ix[i, 'modern_lat'] = ty[0]
        unknown.ix[i, 'modern_lon'] = ty[1]
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
