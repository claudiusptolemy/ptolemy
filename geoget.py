import sys
import requests
import urllib

base_url = "http://maps.googleapis.com/maps/api/geocode/json"

if len(sys.argv) != 3:
    sys.stderr.write('usage: python geoget.py id "place"\n')

i = sys.argv[1]
p = sys.argv[2]
url = '%s?address=%s' % (base_url, urllib.quote_plus(p))
r = requests.get(url)
g = r.json()
print g['status']
print r.text

with open('../Data/geocode/%s.json' % (i, ), 'w') as f:
    f.write(r.text)


