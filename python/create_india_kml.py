import os
import glob
import re
import csv
import argparse

import simplekml
from string import Template

DESC_TEMPLATE_TEXT = """\
<table>
<tr><td>Name</td><td>$name</td></tr>
<tr><td>Page</td><td>$page</td></tr>
<tr><td>Line</td><td>$line</td></tr>
<tr><td>Longitude</td><td>$lon</td></tr>
<tr><td>Latitude</td><td>$lat</td></tr>
<tr><td>Text</td><td>$text</td></tr>
</table>"""

DESC_TEMPLATE = Template(DESC_TEMPLATE_TEXT)

def max_cdots(line):
    mdots = 0
    cdots = 0
    for c in line:
        if c == '.':
            cdots += 1
        elif c == ' ':
            pass
        else:
            if cdots > mdots:
                mdots = cdots
            cdots = 0
    return mdots

def cdot_regs(line, lim):
    regs = []
    cdots = 0
    start = None
    stop = None
    cnum = 0
    for c in line:
        cnum += 1
        if c == '.':
            cdots += 1
            if start is None:
                start = cnum
            stop = cnum
        elif c == ' ':
            pass
        else:
            if cdots >= lim:
                regs.append((start, stop))
                start = stop = None
            cdots = 0
    return regs

numr1 = re.compile('.*?(\d+).*?')
def parse_mins(text):
    text = text.strip()
    m = numr1.match(text)
    if m:
        return m.group(0)
    else:
        return '0'

rc1 = re.compile(r'^.*?(\d+) *@(.*?)(\d+) *@(.*?)$')
def parse_coords(text):
    text = text.strip()
    text = text.replace('\342\200\231', "'")
    text = text.replace('\302\260', "@")
    text = text.replace('l', '1')
    m = rc1.match(text)
    if m:
        ad, am, bd, bm = m.groups()
        am = parse_mins(am)
        bm = parse_mins(bm)
        return ad, am, bd, bm
    else:
        return '<parse error>'

def parse_line(line):
    regs = cdot_regs(line, 3)
    if not regs:
        return None
    d1 = regs[0][0]
    d2 = regs[-1][1]
    return line[0:(d1-1)].strip(), line[(d2+1):]

def dms_to_dec(dms):
    dec = float(dms[0])
    if len(dms) >= 2:
        dec += float(dms[1]) / 60.0
    if len(dms) >= 3:
        dec += float(dms[2]) / 3600.0
    return dec

def txt(text):
    return text.decode('us-ascii', 'ignore')

class Loc(object):
    def __init__(self, page, line, name, lon, lat, text):
        self.page = page
        self.line = line
        self.name = txt(name)
        self.lon = lon
        self.lat = lat
        self.text = txt(text)
    def __getitem__(self, name):
        return getattr(self, name)

def parse_loc(page_num, line_num, line):
    name, coords_text = parse_line(line)
    coords = parse_coords(coords_text)
    if coords == '<parse error>':
        return None
    try:
        lon = dms_to_dec(coords[0:2])
        lat = dms_to_dec(coords[2:4])
        return Loc(page_num, line_num, name, lon, lat, line)
    except ValueError, e:
        return None

def read_locs_dir(dir_path):
    locs = []
    for filename in glob.glob(dir_path):
        page_num = int(filename[11:14])
        line_num = 0
        with open(filename, 'r') as infile:
            for line in infile:
                line_num += 1
                line = line.strip()
                dots = max_cdots(line)
                if dots > 3:
                    loc = parse_loc(page_num, line_num, line)
                    if loc:
                        locs.append(loc)
    return locs

def write_locs_csv(filename, locs):
    with open(filename, 'wb') as outfile:
        writer = csv.writer(outfile)
        for loc in locs:
            row = [loc.page, loc.line, loc.name, loc.lon, loc.lat, loc.text]
            writer.writerow(row)

def write_locs_kml(kml_name, locs):
    """Writes out a KML file based on a list of location objects."""
    kml = simplekml.Kml()
    for loc in locs:
        p = kml.newpoint(
            name=loc.name.decode('us-ascii', 'ignore'),
            coords=[(loc.lon, loc.lat)],
            description=DESC_TEMPLATE.substitute(loc))
        #p.style.iconstyle.color = loc.object_status_color
    kml.save(kml_name)
    
if __name__ == '__main__':
    locs = read_locs_dir('india/*.txt')
    write_locs_csv('india.csv', locs)
    write_locs_kml('india.kml', locs)
