# Given the .tab files from Stuckelberger and Grasshoff, some associated
# metadata and translation files, prepare a training set we can use to 
# prepare a model.

import logging

import csv
import sgdb
import geocode

logging.basicConfig(level='DEBUG')

sg = sgdb.get_instance()
print 'loaded sgdb'
print 'place count: %d' % len(sg.places)

def print_places():
    for p in sg.places:
        try:
            geo = geocode.get_geocoding(p.ptol_id)
            if geo.good:
                geostat = 'Good'
            else:
                geostat = 'Kinda'
        except IOError:
            geostat = 'Missing'
        except ValueError:
            geostat = 'Error'
        if geostat == 'Good':
            print p.ptol_id, geostat, geo.lat, geo.lng

print_places()
