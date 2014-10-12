# common.py
# Contains the common configuration constants and function definitions
# for the various place estimation modules we are trying for the Ptolemy
# project.

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

def write_line(kml, coords, color):
    ls = kml.newlinestring(name="", description="", coords=coords)
    ls.tessellate = 1
    ls.altitudemode = simplekml.AltitudeMode.clamptoground
    ls.style.linestyle.width = 1
    ls.style.linestyle.color = color

def write_three_lines(kml, places, source_prefix, dest_suffix, color):
    source_lon_col = source_prefix + '_lon'
    source_lat_col = source_prefix + '_lat'
    prefixes = ['a','b','c']
    dest_lon_cols = ['%s%s_lon' % (pre, dest_suffix) for pre in prefixes]
    dest_lat_cols = ['%s%s_lat' % (pre, dest_suffix) for pre in prefixes]
    for i, p in places.iterrows():
        source_lon = p[source_lon_col]
        source_lat = p[source_lat_col]
        for j in range(len(prefixes)):
            dest_lon = p[dest_lon_cols[j]]
            dest_lat = p[dest_lat_cols[j]]
            coords = [(source_lon,source_lat), (dest_lon,dest_lat)]
            write_line(kml, coords, color)

def write_kml_file(filename, tri, known, unknown):
    """Write the KML file for the triangulation."""
    kml = simplekml.Kml()
    write_points(kml, known, 'ptol_id', 'ptol_lon', 'ptol_lat', 'ff0000ff')
    write_points(kml, known, 'ptol_id', 'modern_lon', 'modern_lat', 'ff00ffff')
    if tri:
        write_lines(kml, tri, known, 'ptol_lon', 'ptol_lat', 'ff0000ff')
        write_lines(kml, tri, known, 'modern_lon', 'modern_lat', 'ff00ffff')
    else:
        write_three_lines(kml, unknown, 'ptol', 'x', '660099ff')
        write_three_lines(kml, unknown, 'modern', 'y', '6600ff00')
    write_points(kml, unknown, 'ptol_id', 'ptol_lon', 'ptol_lat', 'ff0099ff')
    write_points(kml, unknown, 'ptol_id', 'modern_lon', 'modern_lat', 'ff00ff00')
    kml.save(filename)
