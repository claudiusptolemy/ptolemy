# regression_measure.py: Predict modern coordinates for places
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
from sklearn.cross_validation import LeaveOneOut

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
places.reindex(columns=['ptol_id'])
places = places.loc[pd.notnull(places.ptol_lat), :]
places = places.loc[:, KEY_PLACE_FIELDNAMES]
places = places.loc[places.ptol_id.str.startswith(TARGET_BOOK), :]
places = pd.merge(places, geocode.read_geocodes(), how='left')
known = places.loc[pd.notnull(places.modern_lat), :]
known.is_copy = False
known.to_csv('../Data/regression_measure_before.csv', encoding='cp1252')

loo = LeaveOneOut(len(known))
for train, test in loo:
    trainx = known.iloc[train, :].loc[:, X_NAMES]
    testx = known.iloc[test, :].loc[:, X_NAMES]
    lonreg = linear_model.LinearRegression()
    latreg = linear_model.LinearRegression()
    lonreg.fit(trainx, known.iloc[train, :].modern_lon)
    latreg.fit(trainx, known.iloc[train, :].modern_lat)
    known.loc[known.iloc[test,:].index, 'pred_lat'] = latreg.predict(testx)
    known.loc[known.iloc[test,:].index, 'pred_lon'] = lonreg.predict(testx)

known.to_csv('../Data/regression_measure.csv', encoding='cp1252')

