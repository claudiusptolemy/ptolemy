# convert_xls_to_kml.py
#
# From prior work, Dmitri and his prior colleague already had
# a spreadsheet that contained the Ptolemaic and modern names
# and locations for many places of interest. This script reads
# in that spreadsheet and converts it to a KML file. This serves
# as a prototype and proof of concept of writing the KML file,
# and may help in our further analysis.

import argparse
import xlrd
import simplekml

from location import Location

# List of columns corresponding to the header in the 
# sheets we are reading for this.
CNAMES = [
    'ptol_name',
    'modern_lat',
    'modern_lon',
    'object_type',
    'ptol_lon_dms',
    'ptol_lat_dms',
    'ptol_lat',
    'ptol_lon',
    'modern_name',
    'object_status',
    'status_code']


def read_locations(wb_name, sheet_name):
    """Read all the locations in the Excel workbook called wbname
    and return them as a list of Location objects."""
    wb = xlrd.open_workbook(wb_name)
    sheet = wb.sheet_by_name(sheet_name)
    locations = []
    for r in range(1,sheet.nrows):
        row = dict(zip(CNAMES, [sheet.cell_value(r,c) for c in range(sheet.ncols)]))
        locations.append(Location(**row))
    return locations


def write_kml(kml_name, locations):
    """Writes out a KML file based on a list of location objects."""
    kml = simplekml.Kml()
    for loc in locations:
        p = kml.newpoint(
            name=loc.modern_name,
            coords=[loc.modern_coords],
            description=loc.description)
        p.style.iconstyle.color = loc.object_status_color
    kml.save(kml_name)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-b', '--workbook', help='', required=True)
    parser.add_argument('-k', '--kml', help='', required=True)
    parser.add_argument('-s', '--sheet', help='', required=True)
    args = parser.parse_args()
    write_kml(args.kml, read_locations(args.workbook, args.sheet))
