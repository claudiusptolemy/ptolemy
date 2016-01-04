# predict.py
# This file is part of the Ptolemy Layer for Google Earth project.
# It provides a common way to run the prediction part against any
# of our models.

import os
import sys
import argparse

import common

XCOLS = ['ptol_%s' % s for s in ('lat', 'lon')]
YCOLS = [s.replace('ptol', 'modern') for s in XCOLS]

def main(filename, model, places):
    known, unknown = common.split_places(places)
    knownX = known.loc[:, XCOLS]
    knownY = known.loc[:, YCOLS]
    model.fit(knownX, knownY)
    unknownX = unknown.loc[:, XCOLS]
    unknownY = model.predict(unknownX)
    unknown.loc[:,YCOLS] = unknownY
    common.write_kml_file(filename, None, known, unknown)
    common.write_csv_file(filename[0:-4]+'.csv', known, unknown)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Predict unknown Ptolemy places.')
    parser.add_argument('--model', help='prediction model to use')
    parser.add_argument('--sgdb', help='read from sgdb with given prefix')
    parser.add_argument('--xlsx', help='xlsx to read from instead of sgdb')
    parser.add_argument('--output', help='output filename')
    
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
        output = os.path.join(common.PTOL_HOME, 'Data', '%s.kml' % args.model)

    main(output, model, places)
