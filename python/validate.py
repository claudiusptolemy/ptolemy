# measure.py: Predict modern coordinates for places
# described by Ptolemy using any of our models.

import os
import sys
import argparse

from sklearn.cross_validation import LeaveOneOut
from geopy.distance import vincenty

import common
import bayesian_adjust

from predict import XCOLS, YCOLS

PCOLS = [s.replace('ptol', 'pred') for s in XCOLS]


def validate_each(known, model, prior):
    loo = LeaveOneOut(len(known))
    for train, test in loo:
        trainx = known.iloc[train, :].loc[:, XCOLS]
        trainy = known.iloc[train, :].loc[:, YCOLS]
        testx = known.iloc[test, :].loc[:, XCOLS]
        model.fit(trainx, trainy)
        testy = model.predict(testx)
        plat, plon = testy[0]
        known.loc[known.iloc[test, :].index, 'pred_lat'] = plat
        known.loc[known.iloc[test, :].index, 'pred_lon'] = plon
        if prior:
            alat, alon = prior.adjust_point(plat, plon)
            known.loc[known.iloc[test, :].index, 'adjust_lat'] = alat
            known.loc[known.iloc[test, :].index, 'adjust_lon'] = alon


def compute_errors(known):
    for i, p in known.iterrows():
        modern_coords = (p.modern_lat, p.modern_lon)

        lat_err = p.modern_lat - p.pred_lat
        lon_err = p.modern_lon - p.pred_lon
        sq_err = lat_err ** 2 + lon_err ** 2
        pred_coords = (p.pred_lat, p.pred_lon)
        dist_err = vincenty(modern_coords, pred_coords).kilometers
        known.loc[i, 'lat_err'] = lat_err
        known.loc[i, 'lon_err'] = lon_err
        known.loc[i, 'sq_err'] = sq_err
        known.loc[i, 'dist_err'] = dist_err

        adjust_lat_err = p.modern_lat - p.adjust_lat
        adjust_lon_err = p.modern_lon - p.adjust_lon
        adjust_sq_err = adjust_lat_err ** 2 + adjust_lon_err ** 2
        modern_coords = (p.modern_lat, p.modern_lon)
        adjust_coords = (p.adjust_lat, p.adjust_lon)
        adjust_dist_err = vincenty(modern_coords, adjust_coords).kilometers
        known.loc[i, 'adjust_lat_err'] = adjust_lat_err
        known.loc[i, 'adjust_lon_err'] = adjust_lon_err
        known.loc[i, 'adjust_sq_err'] = adjust_sq_err
        known.loc[i, 'adjust_dist_err'] = adjust_dist_err

        known.loc[i, 'adjust_dist_err_diff'] = dist_err - adjust_dist_err


def main(output, model, places, prior):
    known, unknown = common.split_places(places)
    validate_each(known, model, prior)
    compute_errors(known)
    known.to_csv(output, encoding='utf-8')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
            description='Validate model with known Ptolemy places.')
    parser.add_argument('--model', help='prediction model to use', required=True)
    parser.add_argument('--sgdb', help='read from sgdb with given prefix')
    parser.add_argument('--xlsx', help='xlsx to read from instead of sgdb')
    parser.add_argument('--output', help='output filename')
    parser.add_argument('--prior', required=True,
                        help='an image file representing the prior')
    parser.add_argument('--resolution', default=720, type=int,
                        help='resolution for the grid approximation')
    parser.add_argument('--lower_left_lon', type=float,
                        help='latitude for the lower left coordinate')
    parser.add_argument('--lower_left_lat', type=float,
                        help='latitude for the lower left coordinate')
    parser.add_argument('--upper_right_lon', type=float,
                        help='longitude for the upper right coordinate')
    parser.add_argument('--upper_right_lat', type=float,
                        help='latitude for the upper right coordinate')

    args = parser.parse_args()

    model = common.construct_model(args.model)

    if args.sgdb:
        places = common.read_places(args.sgdb)
    elif args.xlsx:
        places = common.read_places_xlsx(args.xlsx)
    else:
        sys.stderr.write('must specify one of --sgdb or --xlsx')
        exit(1)

    if args.output:
        output = args.output
    else:
        output = os.path.join(common.PTOL_HOME, 'Data', 'validate_%s.csv' % args.model)

    lower_left_coord = (30, 10)
    upper_right_coord = (60, 40)
    prior_filename = args.prior
    lon_lim = args.lower_left_lon, args.upper_right_lon
    lat_lim = args.upper_right_lat, args.lower_left_lat
    res = args.resolution
    prior = bayesian_adjust.ImagePrior(prior_filename, lat_lim, lon_lim, res)


    main(output, model, places, prior)
