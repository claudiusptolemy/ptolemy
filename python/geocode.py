import os
import json
import logging
import pandas as pd

PTOL_HOME = os.environ['PTOL_HOME']
GEOCODE_HOME = os.path.join(PTOL_HOME, 'Data', 'geocode')
SUFFIX = 'json'

class Geocoding(object):

    def __init__(self, ptol_id, data):
        self.ptol_id = ptol_id
        self.data = data

    @property
    def good(self):
        return 'results' in self.data and len(self.data['results']) > 0

    @property
    def lat(self):
        return self.data['results'][0]['geometry']['location']['lat']

    @property
    def lng(self):
        return self.data['results'][0]['geometry']['location']['lng']

    def to_panda_dict_row(self):
        row = {}
        row['ptol_id'] = self.ptol_id
        row['modern_lat'] = self.lat
        row['modern_lon'] = self.lng
        return row
        

def get_geocoding(ptol_id):
    filename = '%s.%s' % (ptol_id, SUFFIX)
    with open(os.path.join(GEOCODE_HOME, filename), 'r') as jsonfile:
        jsontext = jsonfile.read()
        jsondata = json.loads(jsontext)
        return Geocoding(ptol_id, jsondata)

def read_geocodes():
    places = []
    filenames = os.listdir(GEOCODE_HOME)
    for filename in filenames:
        ptol_id = filename[:-5]
        try:
            geo = get_geocoding(ptol_id)
            if geo.good:
                places.append(geo.to_panda_dict_row())
        except ValueError as e:
            print ptol_id, e
    return pd.DataFrame(places)
