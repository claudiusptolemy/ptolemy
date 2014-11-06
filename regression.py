# regression.py: Predict modern coordinates for places
# described by Ptolemy using linear regression against
# the places that have been suggested by other means.

import os
import sys
import csv
import random
import logging

import simplekml
import numpy as np
import pandas as pd
from sklearn import linear_model

import sgdb
import geocode
import common

X_NAMES = [
    'ptol_lat',
    'ptol_lon']

def derive_unknown_modern_coords(known, unknown):
    trainx = known.loc[:, X_NAMES]
    unknownx = unknown.loc[:, X_NAMES]
    lonreg = linear_model.LinearRegression()
    latreg = linear_model.LinearRegression()
    lonreg.fit(trainx, known.modern_lon)
    latreg.fit(trainx, known.modern_lat)
    unknown.is_copy = False # prevent warning below that it's a copy of places
    unknown.loc[:,'modern_lon'] = lonreg.predict(unknownx)
    unknown.loc[:,'modern_lat'] = latreg.predict(unknownx)

def main(filename):
    places = common.read_places()
    known, unknown = common.split_places(places)
    derive_unknown_modern_coords(known, unknown)
    common.write_kml_file(filename, None, known, unknown)
    common.write_csv_file(filename[0:-4]+'.csv', known, unknown)

if __name__ == '__main__':
    filename = sys.argv[1]
    main(filename)
