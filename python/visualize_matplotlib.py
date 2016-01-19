import sys
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import argparse


def read_files(filenames):
    return pd.concat([pd.read_csv(f) for f in filenames])


def draw_map(filenames, title):
    data = read_files(filenames)
    enlarge_by = 0.1
    plt.figure(num=None, figsize=(8, 8), dpi=96, facecolor='w', edgecolor='k')
    data = data.loc[data.modern_lat != 0.0, :]
    ll = data.modern_lat.min(), data.modern_lon.min(),
    ur = data.modern_lat.max(), data.modern_lon.max(),
    print ll, ur
    adj = tuple((ur[i] - ll[i]) * enlarge_by for i in range(2))
    ll = tuple(ll[i] - adj[i] for i in range(2))
    ur = tuple(ur[i] + adj[i] for i in range(2))
    lat0 = ll[0] + ((ur[0] - ll[0]) / 2.0)
    lon0 = ll[1] + ((ur[1] - ll[1]) / 2.0)
    print ll, ur, adj, lat0, lon0
    bmap = Basemap(projection='merc', resolution='l',
                   lon_0=lon0,
                   lat_0=90.0, lat_ts=lat0,
                   llcrnrlat=ll[0],
                   llcrnrlon=ll[1],
                   urcrnrlat=ur[0],
                   urcrnrlon=ur[1])
    bmap.shadedrelief()
    bmap.drawmapboundary()
    bmap.drawmeridians(np.arange(0, 360, 5), labels=[0, 0, 0, 1], fontsize=10)
    bmap.drawparallels(np.arange(-90, 90, 5), labels=[1, 0, 0, 0], fontsize=10)
    bmap.drawcounties(linewidth=1)
    for disp, col in [('known', 'c'), ('unknown', 'm'), ('tentative', 'b')]:
        i = data.disposition == disp
        lats = [lat for lat in list(data.loc[i, 'modern_lat']) if lat != 0.0]
        lons = [lon for lon in list(data.loc[i, 'modern_lon']) if lon != 0.0]
        x, y = bmap(lons, lats)
        bmap.scatter(x, y, 8, marker='o', color=col)
    plt.title(title)
    plt.show()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Show a map of the results of the prediction.')
    parser.add_argument('filenames', nargs='+', help='csv file(s) produced by the model to be shown')
    args = parser.parse_args()
    title = 'Ptolemy\'s Geography in Modern Coordinates'  # TODO auto generate or pass as parameter
    draw_map(args.filenames, title)