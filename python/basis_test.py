from numpy import linalg
import numpy as np
import pandas as pd
import simplekml

from triangulate import write_points

XCOLS = ['xlon', 'xlat']
YCOLS = ['ylon', 'ylat']

RED = 'ff0000ff'
YELLOW = 'ff00ffff'

def coords(data, cols, name):
    return data.loc[data.name == name, cols].values[0]

def multi_coords(data, cols, names):
    return tuple(coords(data, cols, name) for name in names)

def change_basis(ax, bx, cx, tx, ay, by, cy):
    px = ax - cx
    qx = bx - cx
    rx = tx - cx
    A = np.matrix(np.column_stack([px, qx]))
    rv = linalg.solve(A, rx)
    py = ay - cy
    qy = by - cy
    B = np.matrix(np.column_stack([py, qy]))
    ry = np.array((B * np.matrix(rv).transpose()).transpose())[0]
    ty = ry + cy
    return ty

def show_points(points):
    for x in points:
        print x

def add_point(kml, name, coords, color):
    p = kml.newpoint(name=name, coords=[coords])
    p.style.iconstyle.color = color

def load_data(filename):
    data = pd.read_csv(filename)
    data.loc[:, 'xlat'] = (data.ylat - 1.08) * 1.01
    data.loc[:, 'xlon'] = (data.ylon + 1.32) * 1.02
    return data

def write_kml(filename, ax, bx, cx, tx, ay, by, cy, ty):
    kml = simplekml.Kml()
    add_point(kml, 'ax', ax, RED)
    add_point(kml, 'bx', bx, RED)
    add_point(kml, 'cx', cx, RED)
    add_point(kml, 'tx', tx, RED)
    add_point(kml, 'ay', ay, YELLOW)
    add_point(kml, 'by', by, YELLOW)
    add_point(kml, 'cy', cy, YELLOW)
    add_point(kml, 'ty', ty, YELLOW)
    kml.save(filename)

def main():
    data = load_data('../Data/indiana.csv')
    print data
    names = ('Indianapolis', 'Bloomington', 'Columbus', 'Trafalgar')
    ax, bx, cx, tx = multi_coords(data, XCOLS, names)
    ay, by, cy, ty = multi_coords(data, YCOLS, names)
    ty = change_basis(ax, bx, cx, tx, ay, by, cy)
    write_kml('../Data/indiana.kml', ax, bx, cx, tx, ay, by, cy, ty)

if __name__ == '__main__':
    main()


