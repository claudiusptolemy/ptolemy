# predict.py
# This file is part of the Ptolemy Layer for Google Earth project.
# It provides a common way to run the prediction part against any
# of our models.

import os
import sys

import common

XCOLS = ['ptol_%s' % s for s in ('lat', 'lon')]
YCOLS = [s.replace('ptol', 'modern') for s in XCOLS]

def main(filename, model):
    places = common.read_places()
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
    modelname = sys.argv[1]
    model = common.construct_model(modelname)
    filename = os.path.join(common.PTOL_HOME, 'Data', '%s.kml' % modelname)
    main(filename, model)
