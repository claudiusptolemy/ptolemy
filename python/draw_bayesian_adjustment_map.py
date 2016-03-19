import sys
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import argparse


def draw_map(outfilename, dpi):
    enlarge_by = 0.1
    plt.figure(num=None, figsize=(48, 48), dpi=dpi, facecolor='w', edgecolor='k')
    bmap = Basemap(projection='cyl', resolution='l',
                   lon_0=0.0,
                   lat_0=90.0, lat_ts=0.0,
                   llcrnrlat=10,
                   llcrnrlon=30,
                   urcrnrlat=40,
                   urcrnrlon=60)
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
    args = parser.parse_args()
    title = 'Ptolemy\'s Geography in Modern Coordinates'  # TODO auto generate or pass as parameter
    draw_map(args.output, args.dpi)