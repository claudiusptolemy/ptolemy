# regression.py: Predict modern coordinates for places
# described by Ptolemy using linear regression against
# the places that have been suggested by other means.

import os
import csv
import random
import logging

import simplekml
import numpy as np
import pandas as pd
from sklearn import linear_model

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

X_NAMES = [
    'ptol_lat',
    'ptol_lon']

TARGET_BOOK = '7' # book 7 contains India

places = sgdb.read_places().drop_duplicates('ptol_id')
places = places.loc[pd.notnull(places.ptol_lat), :]
places = places.loc[:, KEY_PLACE_FIELDNAMES]
places = places.loc[places.ptol_id.str.startswith(TARGET_BOOK), :]
places = pd.merge(places, geocode.read_geocodes(), how='left')
known = places.loc[pd.notnull(places.modern_lat), :]
unknown = places.loc[pd.isnull(places.modern_lat), :]

trainx = known.loc[:, X_NAMES]
unknownx = unknown.loc[:, X_NAMES]

lonreg = linear_model.LinearRegression()
latreg = linear_model.LinearRegression()
lonreg.fit(trainx, known.modern_lon)
latreg.fit(trainx, known.modern_lat)
unknown.is_copy = False # prevent warning below that it's a copy of places
unknown.loc[:,'modern_lon'] = lonreg.predict(unknownx)
unknown.loc[:,'modern_lat'] = latreg.predict(unknownx)

def enc(s):
    try:
        a = s.encode('ascii','ignore')
        a = ''.join(c for c in a if ord(c)>32 and ord(c)<124)
        return a
    except:
        return 'error'

kml = simplekml.Kml()
for i, r in unknown.iterrows():
    p = kml.newpoint(
        name=enc(r.ptol_name),
        coords=[(r.modern_lon, r.modern_lat)])
    p.style.iconstyle.color = 'ff0000ff'
kml.save(os.path.join(PTOL_HOME, 'Data', 'ptolemy.kml'))
