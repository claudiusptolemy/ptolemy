# bayesian_one.py: Initial attempt at getting a Bayesian
# prior in and a posterior out for the Ptolemy problem.

import sys
import os
import csv
import random
import logging

import simplekml
import numpy as np
import pandas as pd
from numpy import linalg
from sklearn import linear_model

from scipy.stats import multivariate_normal
import skimage
from skimage import exposure
from skimage import io
from skimage import data, filter
import Image
from geopy.distance import vincenty
import matplotlib.pyplot as plt

import sgdb
import geocode

PTOL_HOME = os.environ['PTOL_HOME']
logging.basicConfig(level='DEBUG')

# plt.imshow(check, cmap='gray', interpolation='nearest')
# camera = data.camera()
# filtered_camera = filter.median_filter(camera)
# filtered_camera = filter.gaussian_filter(camera, 1)
# filename = os.path.join(skimage.data_dir, 'camera.png')
# logo = io.imread('http://scikit-image.org/_static/img/logo.png')
# io.imsave('C:/Users/Corey/Desktop/local_logo.png', logo)
# lena = data.lena()
# plt.imshow(lena)
# plt.imshow(lena, interpolation='nearest', cmap='gray')
# text = data.text()
# hsobel_text = filter.hsobel(text)
# plt.imshow(text)
# plt.imshow(hsobel_text)
# filename = 'C:/Users/Corey/Dropbox/Learning/CNIT499/Images/portvein777india_2013-02-17.jpg'
# india = io.imread(filename)
# plt.imshow(india)

# x = np.linspace(0, 5, 10, endpoint=False)
# y = multivariate_normal.pdf(x, mean=2.5, cov=0.5); y
# plt.plot(x, y)
# var = multivariate_normal(mean=[0,0], cov=[[1,0],[0,1]])
# var.pdf([1,0])

# 5340-4351
# 3363-2374
# 2374-1385
# 1385-397

# 4744-3755
# 3755-2767
# 2767-1779
# 1779-790
# india.shape

# 5732-5340
# 392/988.5
# (392/988.5)*5
# 10.0-(392/988.5)*5
# 35.0+(397/988.5)*5
# 70.0-(790/988.5)*5
# 4923-4744
# 90.0+(179/988.5)*5

def load_image(filename):
    return io.imread(os.path.join(PTOL_HOME, 'Images', filename))

def load_gray_image(filename):
    image = load_image(filename)
    return skimage.color.rgb2gray(image)

def save_image(filename, image):
    io.imsave(os.path.join(PTOL_HOME, 'Images', filename), image)

# prior1 = io.imread('C:/Users/Corey/Dropbox/Learning/CNIT499/Images/base_prior_02.png')
# prior2 = skimage.color.rgb2gray(prior1)
# prior3 = prior2 / sum(prior2)
# io.imsave('C:/Users/Corey/Desktop/prior3.png', prior3)

# mean = [0,0]
# cov = [[1,0],[0,100]]
# x,y = np.random.multivariate_normal(mean, cov, 5000).T
# plt.plot(x,y,'x'); plt.axis('equal'); plt.show()

# x = np.linspace(0, 5, 10, endpoint=False)
# y = multivariate_normal.pdf(x, mean=2.5, cov=0.5)
# plt.plot(x, y)
# x, y = np.mgrid[-1:1:.01, -1:1:.01]
# pos = np.empty(x.shape + (2,))
# pos[:, :, 0] = x
# pos[:, :, 1] = y
# rv = multivariate_normal([0.5, -0.2], [[2.0, 0.3], [0.3, 0.5]])
# plt.contourf(x, y, rv.pdf(pos))

def save_prob_image(p1, filename):
    pim = p1 * (1/p1.max())
    # plt.imshow(pim)
    save_image(filename, pim)

def multivariate_point(lat, lon): 
    latlim = (35.0, 5.0)
    latres = 720
    lonlim = (65.0, 95.0)
    lonres = 720
    glat = np.tile(np.linspace(latlim[0],latlim[1],latres),(latres,1))
    glon = np.tile(np.linspace(lonlim[0],lonlim[1],lonres),(lonres,1)).transpose()
    grid = np.empty(glon.shape + (2,))
    grid[:,:,0] = glat
    grid[:,:,1] = glon
    print grid
    rv = multivariate_normal([lat, lon])
    prob = rv.pdf(grid)
    prob = prob / prob.sum()
    return prob.transpose()

# x,y = np.mgrid[65:95:(1/24.0), 35:5:(1/24.0)]
# x,y = np.mgrid[65:95:(1/24.0), 5:35:(1/24.0)]
# z = np.empty(x.shape + (2,))
# z[:,:,0] = x
# z[:,:,1] = y
# rv = multivariate_normal([75.0, 20.0])
# p1 = rv.pdf(z)
# pim = p1 * (1/p1.max())
# plt.imshow(pim)
# plt.imshow(pim, interpolation='nearest', cmap='gray')
# plt.imshow(pim, cmap='gray')
# rv2 = multivariate_normal([77.5, 22.5])
# p2 = rv2.pdf(z)
# pim2 = p2 * (1/p2.max())
# plt.imshow(pim2, cmap='gray')
# pim3 = pim1 * pim2
# plt.imshow(pim3, cmap='gray')
# p2 = p2 / p2.sum()
# p3 = p1 * p2
# p3 = p3 / p3.sum()
# pim3 = p3 * (1/p3.max())
# plt.imshow(pim3, cmap='gray')

# r = multivariate_normal()
# p4 = rv.pdf(z, [80.0, 15.0])
# p4 = multivariate_normal.pdf(z, [80.0, 15.0])
# p4 = multivariate_normal.pdf(z, [80.0, 15.0], None)
# p4 = p4 / p4.sum()
# p5 = p3 * p4
# p5 = p5 / p5.sum()
# pim5 = p5 * (1/p5.max())
# plt.imshow(pim5, cmap='gray')
# plt.imshow(prior3)
# plt.imshow(prior3, cmap='gray')
# prior = prior3 / prior3.sum()
# plt.imshow(prior, cmap='gray')
# post = p5 * prior
# post = post / post.sum()
# plt.imshow(post, cmap='gray')

# p6 = multivariate_normal.pdf(z, [85.0, 15.0], None)
# plt.imshow(p6 * prior, cmap='gray')
# p7 = p6 * prior
# p7 = p7 / p7.sum()
# plt.imshow(p7, cmap='gray')

# vincenty((35, 30), (35, 31)).miles / vincenty((0, 30), (0, 31)).miles
# vincenty((15, 30), (15, 31)).miles / 4

def center_mass(p1):
    latlim = (35.0, 5.0)
    latres = 720
    lonlim = (65.0, 95.0)
    lonres = 720
    lat = np.tile(np.linspace(latlim[0],latlim[1],latres),(latres,1)).transpose()
    lon = np.tile(np.linspace(lonlim[0],lonlim[1],lonres),(lonres,1))
    plat = p1 * lat
    plon = p1 * lon
    return plat.sum(), plon.sum()

def grid_to_latlon(g):
    y,x = g
    return ((35.0 - (y / 24.0)), ((x / 24.0) + 65.0))

def map_latlon(prob):
    return grid_to_latlon(np.unravel_index(prob.argmax(), prob.shape))

class ImagePrior(object):

    def __init__(self, image_filename, lat_lim, lon_lim, res):
        self.image_filename = image_filename
        self.lat_lim = lat_lim
        self.lon_lim = lon_lim
        self.res = res
        self.prior = load_gray_image(image_filename)
        nlat = np.linspace(lat_lim[0], lat_lim[1], res)
        glat = np.tile(nlat, (res, 1))
        nlon = np.linspace(lon_lim[0], lon_lim[1], res)
        glon = np.tile(nlon, (res,1)).transpose()
        grid = np.empty(glon.shape + (2,))
        grid[:,:,0] = glat
        grid[:,:,1] = glon
        self.grid = grid

    def adjust_point(self, lat, lon):
        p1 = self.multivariate_point(lat, lon)
        p2 = self.prior * p1
        p2 = p2 / p2.sum()
        #save_prob_image(p1, 'p1.png')
        #save_prob_image(p2, 'p2.png')
        #return center_mass(p1)
        return map_latlon(p1)

    def multivariate_point(self, lat, lon): 
        rv = multivariate_normal([lat, lon])
        prob = rv.pdf(self.grid)
        prob = prob / prob.sum()
        return prob.transpose()

def different(mlat, mlon, alat, alon, epsilon):
    return abs(mlat - alat) >= epsilon or abs(mlon - alon) >= epsilon

def main():
    prior = ImagePrior('prior2.png', (35,5), (65,95), 720)
    csv_filename = os.path.join(PTOL_HOME, 'Data', 'basis.csv')
    with open(csv_filename, 'rb') as csvfile:
        reader = csv.reader(csvfile)
        reader.next()
        for pid, n1, n2, ptype, plat, plon, mlat, mlon in reader:
            if mlat == '' or mlon == '': continue
            mlat, mlon = tuple(float(c) for c in (mlat, mlon))
            alat, alon = prior.adjust_point(mlat, mlon)
            #if different(mlat, mlon, alat, alon, 0.05):
            print '%s %6.2f %6.2f %6.2f %6.2f' % (pid, mlat, mlon, alat, alon)
    #lat1, lon1 = tuple(float(sys.argv[i]) for i in range(1,3))
    #print lat1, lon1
    #lat2, lon2 = prior.adjust_point(lat1, lon1)
    #print lat2, lon2

if __name__ == '__main__':
    main()
