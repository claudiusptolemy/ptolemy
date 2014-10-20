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

def new_point(x, w):
    """Compute a new latitude and longitude coordinate pair by combining the
    three pairs in x according to the weights given in w."""
    return (sum(w[i] * x[i][0] for i in range(3)),
            sum(w[i] * x[i][1] for i in range(3)))

def append_debug_coords(unknown, i, ax, bx, cx, ay, by, cy):
    """Put all the three closest points into the unknown row, both the ptolemy
    coords (the x's) and the modern coords (the y's). This allows us to write 
    them out in the KML and the CSV for troubleshooting."""
    unknown.ix[i, 'ax_lat'] = ax[0]
    unknown.ix[i, 'ax_lon'] = ax[1]
    unknown.ix[i, 'bx_lat'] = bx[0]
    unknown.ix[i, 'bx_lon'] = bx[1]
    unknown.ix[i, 'cx_lat'] = cx[0]
    unknown.ix[i, 'cx_lon'] = cx[1]
    unknown.ix[i, 'ay_lat'] = ay[0]
    unknown.ix[i, 'ay_lon'] = ay[1]
    unknown.ix[i, 'by_lat'] = by[0]
    unknown.ix[i, 'by_lon'] = by[1]
    unknown.ix[i, 'cy_lat'] = cy[0]
    unknown.ix[i, 'cy_lon'] = cy[1]

def derive_unknown_modern_coords(known, unknown):
    """Compute unknown modern coordinates from known ones using the
    given triangulation."""
    X = known.loc[:, XCOLS]
    Y = unknown.loc[:, XCOLS]
    neighbors = NearestNeighbors(n_neighbors=3).fit(X)
    distances, indices = neighbors.kneighbors(Y)
    for i in range(len(unknown)):
        ai, bi, ci = tuple(indices[i,j] for j in range(3))
        ax = known.ix[ai, XCOLS].values
        bx = known.ix[bi, XCOLS].values
        cx = known.ix[ci, XCOLS].values
        tx = unknown.ix[i, XCOLS].values
        ay = known.ix[ai, YCOLS].values
        by = known.ix[bi, YCOLS].values
        cy = known.ix[ci, YCOLS].values
        ty = change_basis(ax, bx, cx, tx, ay, by, cy)
        unknown.ix[i, 'modern_lat'] = ty[0]
        unknown.ix[i, 'modern_lon'] = ty[1]
        append_debug_coords(unknown, i, ax, bx, cx, ay, by, cy)

def find_neighbors(known, unknown):
    """Find 3 neighbors of each unknown point in known."""
    X = known.loc[:, XCOLS]
    Y = unknown.loc[:, XCOLS]
    neighbors = NearestNeighbors(n_neighbors=4, algorithm='ball_tree', metric='haversine').fit(X)
    distances, indices = neighbors.kneighbors(Y)
    print indices
    print distances

def main(filename):
    places = common.read_places()
    known, unknown = common.split_places(places)
    #unknown = unknown.ix[range(5), :]
    derive_unknown_modern_coords(known, unknown)
    common.write_kml_file(filename, None, known, unknown)
    unknown.to_csv('../Data/unknown.csv', encoding='cp1252')

if __name__ == '__main__':
    filename = sys.argv[1]
    main(filename)
