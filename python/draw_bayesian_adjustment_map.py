import sys
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import argparse


def draw_map(outfilename, dpi, lllat, lllon, urlat, urlon):
    enlarge_by = 0.1
    plt.figure(num=None, figsize=(48, 48), dpi=dpi, facecolor='w', edgecolor='k')
    bmap = Basemap(projection='cyl', resolution='l',
                   lon_0=0.0,
                   lat_0=90.0, lat_ts=0.0,
                   llcrnrlat=lllat,
                   llcrnrlon=lllon,
                   urcrnrlat=urlat,
                   urcrnrlon=urlon)
    bmap.shadedrelief()
    #bmap.drawmapboundary()
    #bmap.drawmeridians(np.arange(0, 360, 5), labels=[0, 0, 0, 1], fontsize=10)
    #bmap.drawparallels(np.arange(-90, 90, 5), labels=[1, 0, 0, 0], fontsize=10)
    if outfilename:
        plt.savefig(outfilename, dpi='figure')
    else:
        plt.show()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Show a map of the results of the prediction.')
    parser.add_argument('--output', help='name of the file to be produced')
    parser.add_argument('--dpi', help='dpi of the resulting figure', type=int)
    parser.add_argument('--lower_left_lon', type=float,
                        help='latitude for the lower left coordinate')
    parser.add_argument('--lower_left_lat', type=float,
                        help='latitude for the lower left coordinate')
    parser.add_argument('--upper_right_lon', type=float,
                        help='longitude for the upper right coordinate')
    parser.add_argument('--upper_right_lat', type=float,
                        help='latitude for the upper right coordinate')
    args = parser.parse_args()
    draw_map(args.output, args.dpi, args.lower_left_lat, args.lower_left_lon, args.upper_right_lat, args.upper_right_lon)