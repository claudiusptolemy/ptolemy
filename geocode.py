import os
import json
import logging

PTOL_HOME = os.environ['PTOL_HOME']
GEOCODE_HOME = os.path.join(PTOL_HOME, 'Data', 'geocode')
SUFFIX = 'json'

class Geocoding(object):

    def __init__(self, data):
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

def get_geocoding(place_id):
    filename = '%s.%s' % (place_id, SUFFIX)
    with open(os.path.join(GEOCODE_HOME, filename), 'r') as jsonfile:
        jsontext = jsonfile.read()
        jsondata = json.loads(jsontext)
        return Geocoding(jsondata)
