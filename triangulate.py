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

PTOL_HOME = os.environ['PTOL_HOME']
logging.basicConfig(level='DEBUG')

KEY_PLACE_FIELDNAMES = [
    'ptol_id',
    'ptol_name',
    'ptol_lat',
    'ptol_lon',
    'modern_name']

TARGET_BOOK = '7' # book 7 contains India

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

def read_places():
    """Read places for this script."""
    places = sgdb.read_places().drop_duplicates('ptol_id')
    places = places.loc[pd.notnull(places.ptol_lat), :]
    places = places.loc[:, KEY_PLACE_FIELDNAMES]
    places = places.loc[places.ptol_id.str.startswith(TARGET_BOOK), :]
    places = pd.merge(places, geocode.read_geocodes(), how='left')
    places.set_index('ptol_id', False, False, True, True)
    return places

def split_places(places):
    """Split places into known and unknown places."""
    known = places.loc[pd.notnull(places.modern_lat), :]
    unknown = places.loc[pd.isnull(places.modern_lat), :]
    unknown.is_copy = False # prevent warning below that it's a copy of places
    return known, unknown

def report_places(places):
    """A debugging function to report lat/lon pairs for each place."""
    print places.loc[:, ['ptol_lat','ptol_lon']]

def report_simplices(tri, points):
    """A debugging function to report the triangulation computed."""
    print tri.simplices
    for s in tri.simplices:
        print [(lat, lon) for (lat, lon) in [points.ix[p] for p in s]]

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

def write_points(kml, places, name_col, lon_col, lat_col, color):
    """Write a series of placemarks into kml from places, using the name,
    lon and lat columns specified by the corresponding col parameters, and
    using the specified color."""
    for i, r in places.iterrows():
        p = kml.newpoint(name=r[name_col], coords=[(r[lon_col], r[lat_col])])
        p.style.iconstyle.color = color

def write_lines(kml, tri, places, lon_col, lat_col, color):
    """Write a line for each simplex in tri, each of which refers to
    a point in places by index, using the lat, lon columns specified and
    in the specified color."""
    for s in tri.simplices:
        coords = [(p[lon_col], p[lat_col]) for p in [places.ix[p] for p in s]]
        ls = kml.newlinestring(name="", description="", coords=coords)
        ls.tessellate = 1
        ls.altitudemode = simplekml.AltitudeMode.clamptoground
        ls.style.linestyle.width = 5
        ls.style.linestyle.color = color

def write_kml_file(filename, tri, known, unknown):
    """Write the KML file for the triangulation."""
    kml = simplekml.Kml()
    write_points(kml, known, 'ptol_id', 'ptol_lon', 'ptol_lat', 'ff0000ff')
    write_points(kml, known, 'ptol_id', 'modern_lon', 'modern_lat', 'ff00ffff')
    write_lines(kml, tri, known, 'ptol_lon', 'ptol_lat', 'ff0000ff')
    write_lines(kml, tri, known, 'modern_lon', 'modern_lat', 'ff00ffff')
    write_points(kml, unknown, 'ptol_id', 'ptol_lon', 'ptol_lat', 'ff00ffff')
    write_points(kml, unknown, 'ptol_id', 'modern_lon', 'modern_lat', 'ff00ff00')
    kml.save(filename)

def main(filename):
    places = read_places()
    known, unknown = split_places(places)
    points = known.loc[:, ['ptol_lat','ptol_lon']]
    tri = Delaunay(points, furthest_site=False)
    derive_unknown_modern_coords(tri, known, unknown)
    write_kml_file(filename, tri, known, unknown)

if __name__ == '__main__':
    filename = sys.argv[1]
    main(filename)
