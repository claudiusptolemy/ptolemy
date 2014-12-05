# visualize_neighbors.py
# This file is part of the Ptolemy Layer for Google Earth project.
# It helps us develop our intuition about the path we should be heading
# with model selection by allowing us to visualize how neighbors
# are selected and how the shift under the transformation from Ptolemy
# coordinates to modern coordinates.

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

import sgdb
import geocode
import common


XCOLS = ['ptol_lat','ptol_lon']
YCOLS = ['modern_lat','modern_lon']



def write_point_style(kml, color_name, color_code):
    kml.write('''
        <Style id="%s_point">
            <IconStyle id="substyle_0">
                <color>%s</color>
                <colorMode>normal</colorMode>
                <scale>1</scale>
                <heading>0</heading>
                <Icon id="link_0">
                    <href>http://maps.google.com/mapfiles/kml/pushpin/ylw-pushpin.png</href>
                </Icon>
            </IconStyle>
        </Style>\n''' % (color_name, color_code))

def write_line_style(kml, color_name, color_code):
    kml.write('''
        <Style id="%s_line">
            <LineStyle id="substyle_120">
                <color>%s</color>
                <colorMode>normal</colorMode>
                <width>2</width>
            </LineStyle>
        </Style>\n'''  % (color_name, color_code))

def write_styles(kml):
    colors = [('red', 'ff0000ff'),
              ('orange', 'ff0099ff'),
              ('yellow', 'ff00ffff'),
              ('green', 'ff00ff00'),
              ('cyan', 'ffffff00'),
              ('purple', 'ffff00ff')]
    for name, code in colors:
        write_point_style(kml, name, code)
        write_line_style(kml, name, code)

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

def write_point(kml, style, point):
    kml.write('''
        <Placemark>
            <styleUrl>#%s_point</styleUrl>
            <Point>
                <coordinates>%s,%s,0.0</coordinates>
            </Point>
        </Placemark>''' % (style, point[1], point[0]))

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

def write_point_style(kml, color_name, color_code):
    kml.write('''
        <Style id="%s_point">
            <IconStyle id="substyle_0">
                <color>%s</color>
                <colorMode>normal</colorMode>
                <scale>1</scale>
                <heading>0</heading>
                <Icon id="link_0">
                    <href>http://maps.google.com/mapfiles/kml/pushpin/ylw-pushpin.png</href>
                </Icon>
            </IconStyle>
        </Style>\n''' % (color_name, color_code))

def write_line_style(kml, color_name, color_code):
    kml.write('''
        <Style id="%s_line">
            <LineStyle id="substyle_120">
                <color>%s</color>
                <colorMode>normal</colorMode>
                <width>2</width>
            </LineStyle>
        </Style>\n'''  % (color_name, color_code))

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

def write_line(kml, a, b, color):
    """Write a line for each simplex in tri, each of which refers to
    a point in places by index, using the lat, lon columns specified and
    in the specified color."""
    kml.write('''
        <Placemark>
            <name></name>
            <styleUrl>#%s_line</styleUrl>
            <LineString>
                <extrude>0</extrude>
                <tessellate>1</tessellate>
                <altitudeMode>clampToGround</altitudeMode>
                <coordinates>
                     %f,%f,0
                     %f,%f,0
                </coordinates>
            </LineString>
        </Placemark>\n''' % (color, a[1], a[0], b[1], b[0]))

def write_point(kml, style, point):
    kml.write('''
        <Placemark>
            <styleUrl>#%s_point</styleUrl>
            <Point>
                <coordinates>%s,%s,0.0</coordinates>
            </Point>
        </Placemark>''' % (style, point[1], point[0]))

def write_triangle(kml, name, style, p1, p2, p3):
    kml.write('''
        <Placemark>
            <name>%s</name>
            <styleUrl>#%s_line</styleUrl>
            <LineString>
                <extrude>0</extrude>
                <tessellate>1</tessellate>
                <altitudeMode>clampToGround</altitudeMode>
                <coordinates>
                     %f,%f,0
                     %f,%f,0
                     %f,%f,0
                     %f,%f,0
                </coordinates>
            </LineString>
        </Placemark>\n''' % (name, style,
                             p1[1], p1[0],
                             p2[1], p2[0],
                             p3[1], p3[0],
                             p1[1], p1[0]))
    write_point(kml, 'red', p1)
    write_point(kml, 'yellow', p2)
    write_point(kml, 'green', p3)

def derive_unknown_modern_coords(known, unknown):
    """Compute unknown modern coordinates from known ones using the
    given triangulation."""
    X = known.loc[:, XCOLS]
    Y = unknown.loc[:, XCOLS]
    k = 6 # number of neighbors
    neighbors = NearestNeighbors(n_neighbors=k).fit(X)
    distances, indices = neighbors.kneighbors(X)
    colors = 'red,orange,yellow,green,cyan,purple'.split(',')
    with open('../Data/visualize_neighbors.kml', 'wb') as kml:
        kml.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        kml.write('<kml xmlns="http://www.opengis.net/kml/2.2">\n')
        kml.write('<Document>\n')
        write_styles(kml)
        for i in range(len(known)):
            kml.write('  <Folder id="%s">\n' % (known.ix[i].ptol_id, ))
            kml.write('      <name>%s</name>\n' % (known.ix[i].ptol_id, ))
            ax = known.ix[i, XCOLS].values
            ay = known.ix[i, YCOLS].values
            write_point(kml, 'red', ax)
            write_point(kml, 'red', ay)
            print known.ix[i].ptol_id, ax, ay
            points = tuple(indices[i,j] for j in range(1, k))
            for m in range(len(points)):
                j = points[m]
                bx = known.ix[j, XCOLS].values
                by = known.ix[j, YCOLS].values
                write_point(kml, 'yellow', bx)
                write_point(kml, 'yellow', by)
                write_line(kml, ax, bx, colors[m])
                write_line(kml, ay, by, colors[m])
                print '  ', known.ix[j].ptol_id, bx, by
            #ap, bp, cp = tuple((known.ix[x].ptol_lat, known.ix[x].ptol_lon) for x in simp)
            #write_triangle(kml, tri_name, 'red', ap, bp, cp)
            #am, bm, cm = tuple((known.ix[x].modern_lat, known.ix[x].modern_lon) for x in simp)
            #write_triangle(kml, tri_name, 'yellow', am, bm, cm)
            kml.write('  </Folder>\n')
        kml.write('</Document>\n')
        kml.write('</kml>\n')



def main(filename):
    places = common.read_places()
    known, unknown = common.split_places(places)
    points = known.loc[:, ['ptol_lat','ptol_lon']]
    tri = Delaunay(points, furthest_site=False)
    derive_unknown_modern_coords(known, unknown)
    #derive_unknown_modern_coords(tri, known, unknown)
    #common.write_kml_file(filename, tri, known, unknown)
    #common.write_csv_file(filename[0:-4]+'.csv', known, unknown)

if __name__ == '__main__':
    filename = sys.argv[1]
    main(filename)
