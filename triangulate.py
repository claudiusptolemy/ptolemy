# triangulate.py
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

import sgdb
import geocode
import common

def mgc_distance(a, b, gamma=0.95):
    """Return the modified greatest circle distance based on the radian
    latitude and longitude coordinates a and b in terms of radians, adjusted
    by gamma."""
    return 2.0 * math.asin(min(1, math.sqrt(math.sin(abs(a[0] - b[0])/2.0) ** 2 +
                                            math.cos(a[0]) * math.cos(b[0]) *
                                  math.sin((gamma*abs(a[1] - b[1]))/2.0) ** 2)))

def sphere_tri_area(x):
    """Compute the area of the triangle defined by the three radian
    latitude and longitude coordinate pairs given by x."""
    s = sum(x) / 2.0
    return 4.0 * math.atan(math.sqrt(math.tan(s / 2.0) *
                                     math.tan((s - x[0]) / 2.0) *
                                     math.tan((s - x[1]) / 2.0) *
                                     math.tan((s - x[2]) / 2.0)))

def weights(a, b, c, m):
    """Compute the weights to use for the three latitude and longitude coordinate
    pairs for a, b, and c, to find the coordinate pair m. This can then be used
    to compute a new coordinate pair for m based on alternative coordinates for
    a, b, and c."""
    a, b, c, m = ((math.radians(lat), math.radians(lon)) for (lat, lon) in (a, b, c, m))
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

def derive_unknown_modern_coords(tri, known, unknown):
    """Compute unknown modern coordinates from known ones using the
    given triangulation."""
    simps = tri.find_simplex(unknown.loc[:, ['ptol_lat','ptol_lon']])
    for i in range(len(simps)):
        s = simps[i]
        simp = tri.simplices[s]
        if s > -1:
            p = unknown.ix[i]
            ap, bp, cp = tuple((known.ix[x].ptol_lat, known.ix[x].ptol_lon) for x in simp)
            am, bm, cm = tuple((known.ix[x].modern_lat, known.ix[x].modern_lon) for x in simp)
            mp = (p.ptol_lat, p.ptol_lon)
            w = weights(ap, bp, cp, mp)
            mm = new_point((am, bm, cm), w)
            unknown.loc[p.ptol_id, 'modern_lat'] = mm[0]
            unknown.loc[p.ptol_id, 'modern_lon'] = mm[1]

def main(filename):
    places = common.read_places()
    known, unknown = common.split_places(places)
    points = known.loc[:, ['ptol_lat','ptol_lon']]
    tri = Delaunay(points, furthest_site=False)
    derive_unknown_modern_coords(tri, known, unknown)
    common.write_kml_file(filename, tri, known, unknown)
    common.write_csv_file(filename[0:-4]+'.csv', known, unknown)

if __name__ == '__main__':
    filename = sys.argv[1]
    main(filename)
