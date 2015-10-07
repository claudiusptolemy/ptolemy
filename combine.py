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
    ntrain = 0
    ntrainx = 0
    npredict = 0
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
        if p.ptol_id.startswith('7'):
            if geostat == 'Good':
                print p.ptol_id, geostat, geo.lat, geo.lng, p.ptol_lat, p.ptol_lon
                ntrain += 1
            else:
                if p.ptol_lat != '':
                    #print p.ptol_id, geostat, 'WILL PREDICT'
                    npredict += 1
                    if p.modern_name != '':
                        ntrainx += 1
    print '# to train with current:', ntrain
    print '# to train with to do:', ntrainx
    print '# to train with total:', (ntrainx + ntrain)
    print '# to be predicted:', npredict

print_places()
