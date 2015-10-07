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

def write_neighbor_visualization_kml(known, k=6, verbose=False):
    """Write a KML file showing k nearest neighbors among known locations."""
    X = known.loc[:, XCOLS]
    neighbors = NearestNeighbors(n_neighbors=k).fit(X)
    _, indices = neighbors.kneighbors(X)
    colors = 'red,orange,yellow,green,cyan,purple'.split(',')
    with open('../Data/visualize_neighbors.kml', 'wb') as kml:
        kml.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        kml.write('<kml xmlns="http://www.opengis.net/kml/2.2">\n')
        kml.write('<Document>\n')
        common.write_styles(kml)
        for i in range(len(known)):
            kml.write('  <Folder id="%s">\n' % (known.ix[i].ptol_id, ))
            kml.write('      <name>%s</name>\n' % (known.ix[i].ptol_id, ))
            ax = known.ix[i, XCOLS].values
            ay = known.ix[i, YCOLS].values
            alabel = known.ix[i].ptol_id
            common.write_point(kml, 'red', ax, alabel)
            common.write_point(kml, 'red', ay, alabel)
            if verbose: print known.ix[i].ptol_id, ax, ay
            points = [indices[i,j] for j in range(1, k)]
            for m in range(len(points)):
                j = points[m]
                bx = known.ix[j, XCOLS].values
                by = known.ix[j, YCOLS].values
                blabel = known.ix[j].ptol_id
                common.write_point(kml, 'yellow', bx, blabel)
                common.write_point(kml, 'yellow', by, blabel)
                common.write_line(kml, ax, bx, colors[m])
                common.write_line(kml, ay, by, colors[m])
                if verbose: print '  ', known.ix[j].ptol_id, bx, by
            kml.write('  </Folder>\n')
        kml.write('</Document>\n')
        kml.write('</kml>\n')

if __name__ == '__main__':
    known, _ = common.split_places(common.read_places())
    write_neighbor_visualization_kml(known)
