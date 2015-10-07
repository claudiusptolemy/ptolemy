# measure.py: Predict modern coordinates for places
# described by Ptolemy using any of our models.

import os
import sys
import csv

from sklearn.cross_validation import LeaveOneOut
from geopy.distance import vincenty

import common

from triangulate import Triangulate
from flocking import Flocking
from predict import XCOLS, YCOLS

PCOLS = [s.replace('ptol', 'pred') for s in XCOLS]

def validate_each(known, model):
    loo = LeaveOneOut(len(known))
    for train, test in loo:
        trainx = known.iloc[train, :].loc[:, XCOLS]
        trainy = known.iloc[train, :].loc[:, YCOLS]
        testx = known.iloc[test, :].loc[:, XCOLS]
        model.fit(trainx, trainy)
        testy = model.predict(testx)
        known.loc[known.iloc[test,:].index, 'pred_lat'] = testy[0][0]
        known.loc[known.iloc[test,:].index, 'pred_lon'] = testy[0][1]

def compute_errors(known):
    for i, p in known.iterrows():
        lat_err = p.modern_lat - p.pred_lat
        lon_err = p.modern_lon - p.pred_lon
        sq_err = lat_err ** 2 + lon_err ** 2
        modern_coords = (p.modern_lat, p.modern_lon)
        pred_coords = (p.pred_lat, p.pred_lon)
        dist_err = vincenty(modern_coords, pred_coords).miles
        known.loc[i, 'lat_err'] = lat_err
        known.loc[i, 'lon_err'] = lon_err
        known.loc[i, 'sq_err'] = sq_err
        known.loc[i, 'dist_err'] = dist_err

def main(filename, model):
    places = common.read_places()
    known, unknown = common.split_places(places)
    validate_each(known, model)
    compute_errors(known)
    known.to_csv(filename, encoding='cp1252')

if __name__ == '__main__':
    modelname = sys.argv[1]
    model = common.construct_model(modelname)
    filename = os.path.join(common.PTOL_HOME, 'Data', 'validate_%s.csv' % modelname)
    main(filename, model)
