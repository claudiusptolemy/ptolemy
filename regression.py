# regression.py: Predict modern coordinates for places
# described by Ptolemy using linear regression against
# the places that have been suggested by other means.

import logging
import csv
import numpy as np
from sklearn import linear_model

import sgdb
import geocode

import simplekml

logging.basicConfig(level='DEBUG')

sg = sgdb.get_instance()
print 'loaded sgdb'
print 'place count: %d' % len(sg.places)

pidtr = []
plngtr = []
plattr = []
mlngtr = []
mlattr = []
obtr = []

pidpr = []
plngpr = []
platpr = []
mlngpr = []
mlatpr = []
obpr = []

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
        try:
            if geostat == 'Good':
                if p.ptol_lon != '' and geo.lng != None:
                    pidtr.append(p.ptol_id)
                    plngtr.append(float(p.ptol_lon))
                    plattr.append(float(p.ptol_lat))
                    mlngtr.append(float(geo.lng))
                    mlattr.append(float(geo.lat))
                    obtr.append(p)
                    print p.ptol_id, geostat, geo.lat, geo.lng, p.ptol_lat, p.ptol_lon
            else:
                if p.ptol_lat != '':
                    #print p.ptol_id, geostat, 'WILL PREDICT'
                    pidpr.append(p.ptol_id)
                    plngpr.append(float(p.ptol_lon))
                    platpr.append(float(p.ptol_lat))
                    obpr.append(p)
                    if p.modern_name != '':
                        pass
        except ValueError as v:
            print 'error: ', p.ptol_lon, p.ptol_lat, v

xtrain = np.transpose(np.array([plngtr, plattr]))
ytrainlng = np.transpose(np.array([mlngtr]))
ytrainlat = np.transpose(np.array([mlattr]))
xpred = np.transpose(np.array([plngpr, platpr]))

lngregr = linear_model.LinearRegression()
lngregr.fit(xtrain, ytrainlng)
print 'lngcoef:', lngregr.intercept_, lngregr.coef_

latregr = linear_model.LinearRegression()
latregr.fit(xtrain, ytrainlat)
print 'latcoef:', latregr.intercept_, latregr.coef_

mlngpr = np.transpose(lngregr.predict(xpred)).tolist()[0]
mlatpr = np.transpose(latregr.predict(xpred)).tolist()[0]

print len(pidpr), len(mlngpr), len(mlatpr)
print mlngpr

def enc(s):
    try:
        a = s.encode('ascii','ignore')
        a = ''.join(c for c in a if ord(c)>32 and ord(c)<124)
        return a
    except:
        return 'error'

kml = simplekml.Kml()
for i in range(len(pidtr)):
    p = kml.newpoint(
        name=enc(obtr[i].ptol_name),
        coords=[(mlngtr[i],mlattr[i])],
        description='%s\n%s\n%s,%s' % (pidtr[i], enc(obtr[i].modern_name), plngtr[i], plattr[i]))
    p.style.iconstyle.color = 'ff00ffff'
for i in range(len(pidpr)):
    print enc(obpr[i].ptol_name)
    p = kml.newpoint(
        name=enc(obpr[i].ptol_name),
        coords=[(mlngpr[i],mlatpr[i])],
        description='%s\n%s\n%s,%s' % (pidpr[i], enc(obpr[i].modern_name), plngpr[i], platpr[i]))
    p.style.iconstyle.color = 'ff0000ff'
kml.save('predicted.kml')
