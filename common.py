# common.py
# Contains the common configuration constants and function definitions
# for the various place estimation modules we are trying for the Ptolemy
# project.

import os
import sys
import math
import logging

import numpy as np
import pandas as pd
from geopy.distance import vincenty
from scipy.spatial import Delaunay
from pykml.factory import KML_ElementMaker as KML

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

# book 7 contains India
# chapter 1 is within the Ganges
# chapter 4 is Sri Lanka (mostly)
TARGET_BOOK = '7.01'

def read_places():
    """Read places for this script."""
    places = sgdb.read_places()
    places = places.loc[pd.notnull(places.ptol_lat), :]
    places = places.drop_duplicates('ptol_id')
    places = places.loc[:, KEY_PLACE_FIELDNAMES]
    places = places.loc[places.ptol_id.str.startswith(TARGET_BOOK), :]
    places = pd.merge(places, geocode.read_geocodes(), how='left')
    places.set_index('ptol_id', False, False, True, True)
    return places

def split_places(places):
    """Split places into known and unknown places."""
    known = places.loc[pd.notnull(places.modern_lat), :]
    unknown = places.loc[pd.isnull(places.modern_lat), :]
    # prevent warning below that it's a copy of places
    known.is_copy = False
    unknown.is_copy = False 
    # add disposition column (known vs. unknown)
    known.loc[:, 'disposition'] = 'known'
    unknown.loc[:, 'disposition'] = 'unknown'
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
        placemark_id = 'placemark_%s' % r[name_col]
        point_id = 'point_%s' % r[name_col]
        kml.write('''
        <Placemark id="%s">
            <name>%s</name>
            <styleUrl>#%s_point</styleUrl>
            <Point id="%s">
                <coordinates>%s,%s,0.0</coordinates>
            </Point>
        </Placemark>
''' % (placemark_id, r[name_col], color, point_id, r[lon_col], r[lat_col]))

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

def write_csv_file(filename, known, unknown):
    """Write out a csv file to filename containing all places listed in
    known and unknown. Those to dataframes are merged and sorted by ptol_id
    prior to being written."""
    places = unknown.append(known, True, False)
    places.sort('ptol_id', inplace=True)
    cols = [
        'ptol_id',
        'ptol_name',
        'modern_name',
        'disposition',
        'ptol_lat',
        'ptol_lon',
        'modern_lat',
        'modern_lon',
        'original_lat',
        'original_lon']
    places.to_csv(filename, index=False, encoding='cp1252', columns=cols)

def write_styles(kml):
    kml.write('''
        <Style id="red_point">
            <IconStyle id="substyle_0">
                <color>ff0000ff</color>
                <colorMode>normal</colorMode>
                <scale>1</scale>
                <heading>0</heading>
                <Icon id="link_0">
                    <href>http://maps.google.com/mapfiles/kml/pushpin/ylw-pushpin.png</href>
                </Icon>
            </IconStyle>
        </Style>
        <Style id="yellow_point">
            <IconStyle id="substyle_0">
                <color>ff00ffff</color>
                <colorMode>normal</colorMode>
                <scale>1</scale>
                <heading>0</heading>
                <Icon id="link_0">
                    <href>http://maps.google.com/mapfiles/kml/pushpin/ylw-pushpin.png</href>
                </Icon>
            </IconStyle>
        </Style>
        <Style id="red_line">
            <LineStyle id="substyle_120">
                <color>ff0000ff</color>
                <colorMode>normal</colorMode>
                <width>5</width>
            </LineStyle>
        </Style>''')


def write_kml_file(filename, tri, known, unknown):
    """Write the KML file for the triangulation."""
    with open(filename, 'w') as kml:
        kml.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        kml.write('<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2">\n')
        kml.write('<Document id="ptolemy-7.01">\n')
        write_styles(kml)
    
        write_points(kml, known, 'ptol_id', 'ptol_lon', 'ptol_lat', 'yellow')
        write_points(kml, known, 'ptol_id', 'modern_lon', 'modern_lat', 'yellow')
        #if tri:
        #    write_lines(kml, tri, known, 'ptol_lon', 'ptol_lat', 'ff0000ff')
        #    write_lines(kml, tri, known, 'modern_lon', 'modern_lat', 'ff00ffff')
        #elif 'ax_lon' in unknown:
        #    write_three_lines(kml, unknown, 'ptol', 'x', '660099ff')
        #    write_three_lines(kml, unknown, 'modern', 'y', '6600ff00')
        write_points(kml, unknown, 'ptol_id', 'ptol_lon', 'ptol_lat', 'red')
        write_points(kml, unknown, 'ptol_id', 'modern_lon', 'modern_lat', 'red')
        kml.write('</Document>\n')
        kml.write('</kml>\n')

#        <Style id="stylesel_0">
#            <IconStyle id="substyle_0">
#                <color>ff0000ff</color>
#                <colorMode>normal</colorMode>
#                <scale>1</scale>
#                <heading>0</heading>
#                <Icon id="link_0">
#                    <href>http://maps.google.com/mapfiles/kml/pushpin/ylw-pushpin.png</href>
#                </Icon>
#            </IconStyle>
#        </Style>

#        <Style id="stylesel_120">
#            <LineStyle id="substyle_120">
#                <color>ff0000ff</color>
#                <colorMode>normal</colorMode>
#                <width>5</width>
#            </LineStyle>
#        </Style>


#        <Placemark id="feat_95">
#            <name/>
#            <description/>
#            <styleUrl>#stylesel_93</styleUrl>
#            <LineString id="geom_93">
#                <coordinates>125.0,27.1666666667,0.0 127.0,20.5,0.0 124.0,18.0,0.0</coordinates>
#                <tessellate>1</tessellate>
#                <altitudeMode>clampToGround</altitudeMode>
#            </LineString>
#        </Placemark>

#        <Placemark id="feat_316">
#            <name>7.01.24.02</name>
#            <styleUrl>#stylesel_314</styleUrl>
#            <Point id="geom_314">
#                <coordinates>143.0,24.0,0.0</coordinates>
#            </Point>
#        </Placemark>

