# Given the .tab files from Stuckelberger and Grasshoff, some associated
# metadata and translation files, prepare a training set we can use to 
# prepare a model.

import os
import csv
import logging
import pandas as pd

PTOL_HOME = os.environ['PTOL_HOME']
PTOL_CD = os.path.join(PTOL_HOME, 'Data', 'PtolCD')


PTOL_HOME = os.environ['PTOL_HOME']
DELIMITER = '\t'

SGDB_TABLE_TRANSLATE = {
    'Categories': 'Kategorien',
    'Places': 'Orte',
    'People': 'Personen',
    'Realities': 'Realien'
}

PLACE_FIELDNAMES = [
    'ptol_name',
    'ptol_id',
    'modern_name',
    'category_id',
    'ptol_lat_dms',
    'ptol_lon_dms',
    'category_id_string',
    'map_id',
    'empty1',
    'empty2',
    'x_ptol_lon_dms',
    'x_ptol_lat_dms',
    'time_diff',
    'longest_day',
    'x_time_diff',
    'x_longest_day',
    'sun_zenith_omega',
    'sun_zenith_x',
    'place_catalog_ref',
    'ptol_lon',
    'ptol_lat',
    'empty3',
    'empty4',
    'x_ptol_lon_dec',
    'x_ptol_lat_dec',
    'time_diff_dec',
    'longest_day_dec',
    'x_time_diff_dec',
    'x_longest_day_dec',
    'lon_diff',
    'lat_diff',
    'time_diff_diff',
    'longest_day_diff']

CATEGORY_FIELDNAMES = [
    'category_id',
    'category_id_string',
    'category_name']


class Place(object):
    __slots__ = PLACE_FIELDNAMES
    def __init__(self, d):
        for k, v in d.items():
            setattr(self, k, v)

class SGDB(object):

    def __init__(self):
        self.places = []
        self.places_by_place_id = {}

    def get_place(place_id):
        return self.places_by_place_id[place_id]

def get_filename(table_name):
    filename = '%s.tab' % SGDB_TABLE_TRANSLATE[table_name]
    return os.path.join(PTOL_HOME, 'Data', 'PtolCD', 'dat', filename)

def load_places():
    filename = get_filename('Places')
    logging.debug(filename)
    with open(filename, 'rb') as csvfile:
        reader = csv.DictReader(csvfile, fieldnames=PLACE_FIELDNAMES,
                                delimiter=DELIMITER)
        return [Place(d) for d in reader]

def load_sgdb():
    sgdb = SGDB()
    sgdb.places = load_places()
    logging.debug('loaded places')
    return sgdb

sgdb = None

def get_instance():
    global sgdb
    if sgdb == None:
        sgdb = load_sgdb()
    return sgdb


def read_tab(table, names, encoding):
    filename = os.path.join(PTOL_CD, 'dat', '%s.tab' % table)
    return pd.read_csv(filename, sep='\t', header=-1, names=names, encoding=encoding)

def read_places():
    return read_tab('Orte', PLACE_FIELDNAMES, 'cp1252')

def read_categories():
    filename = os.path.join(PTOL_CD, 'dat', 'Kategorien.tab')
    return read_tab('Kategorien', CATEGORY_FIELDNAMES, 'cp850')
                             
