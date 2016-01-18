#!/usr/bin/python

import os
import argparse

import numpy as np
import pandas as pd
import skimage
from skimage import io
from scipy.stats import multivariate_normal

import common

from common import PTOL_HOME

DESCRIPTION = """
Initial attempt at getting a Bayesian prior in and a
posterior out for the Ptolemy problem.
"""


def load_image(filename):
    """Load an image from the images directory.
    @param filename Name of the file to load.
    """
    return io.imread(os.path.join(PTOL_HOME, 'Images', filename))


def load_gray_image(filename):
    """Load an image from the images directory in grayscale."""
    image = load_image(filename)
    return skimage.color.rgb2gray(image)


def save_image(filename, image):
    """Save an image to the images directory."""
    io.imsave(os.path.join(PTOL_HOME, 'Images', filename), image)


def save_prob_image(p1, filename):
    """Save a probability grid as an image, adjusting so that
    the point with maximum probability is full white."""
    pim = p1 * (1/p1.max())
    save_image(filename, pim)


def coord_space(a, b, res):
    """Create a grid of res values from a to b, repeated res times."""
    return np.tile(np.linspace(a, b, res), (res, 1))


class ImagePrior(object):
    """Represents the state required to adjust predicted Ptolemy
    coordinates using a prior via grid approximation."""

    def __init__(self, image_filename, lat_lim, lon_lim, res):
        self.image_filename = image_filename
        self.lat_lim = lat_lim
        self.lon_lim = lon_lim
        self.res = res
        self.lat_parts = float(res) / abs(lat_lim[0] - lat_lim[1])
        self.lon_parts = float(res) / abs(lon_lim[0] - lon_lim[1])
        self.prior = load_gray_image(image_filename)
        self.glat = coord_space(lat_lim[0], lat_lim[1], res)
        self.glon = coord_space(lon_lim[0], lon_lim[1], res).transpose()
        self.grid = np.empty((res, res, 2))
        self.grid[:,:,0] = self.glat
        self.grid[:,:,1] = self.glon
        
    def multivariate_point(self, lat, lon):
        """Create a grid approximation representation of the
        given lat and lon coordinates. This returns a multivariate
        normal distribution over the grid represented by this state."""
        rv = multivariate_normal([lat, lon])
        prob = rv.pdf(self.grid)
        prob = prob / prob.sum()
        return prob.transpose()

    def center_mass(self, p1):
        """Given the lat/lon in p1 as a grid approximation, find
        the 'center of mass' of the weighted grid to estimate the
        multivariate mean (letting us extract the adjusted point).
        This one seems to give less aestetically pleasing results
        than the map_latlon below."""
        plat = p1 * self.glat.transpose()
        plon = p1 * self.glon.transpose()
        return plat.sum(), plon.sum()

    def grid_to_latlon(self, g):
        """Convert a screen y/x pair in g, convert back to a lat/lon
        pair based on the parameters of the grid approximation state."""
        return ((self.lat_lim[0] - (g[0] / self.lat_parts)),
                ((g[1] / self.lon_parts) + self.lon_lim[0]))

    def map_latlon(self, p):
        """Compute the MAP (maximum a-posteriori) point (i.e., the point
        in the grid with the highest probability), and return the lat/lon
        coordinate pair it represents."""
        return self.grid_to_latlon(np.unravel_index(p.argmax(), p.shape))

    def adjust_point(self, lat, lon, ptol_id=None):
        """Main driver routine which takes in a predicted lat/lon coordinate
        pair, and returns it after adjusting by the given prior. If given
        the ptol_id along with the lat/lon pair, then will render images
        representing the multivariate normal for the point and the posterior
        for debugging purposes. Either map_latlon or center_mass may be 
        specified in the final return statement to adjust the method used
        for the final estimate."""
        if np.isnan(lat) or np.isnan(lon):
            return lat, lon
        else:
            p1 = self.multivariate_point(lat, lon)
            p2 = self.prior * p1
            p2 = p2 / p2.sum()
            if ptol_id:
                save_prob_image(p1, 'prob_%s_p1.png' % ptol_id)
                save_prob_image(p2, 'prob_%s_p2.png' % ptol_id)
            return self.map_latlon(p2)

    def bayesian_adjust(self, p):
        """An adapter routine to make the adjustment method compatible
        with pandas dataframe apply and merge approach."""
        alat, alon = self.adjust_point(p.original_lat, p.original_lon)
        return pd.Series({'modern_lat': alat, 'modern_lon': alon})


def different(mlat, mlon, alat, alon, epsilon):
    """A debugging routine to determine whether the given 2 coordinate
    pairs are different by more than epsilon."""
    return abs(mlat - alat) >= epsilon or abs(mlon - alon) >= epsilon


def bayesian_adjust_file(prior_filename, data_file, output_base, res):
    """Adjust the file given in data file using a Bayesian approach,
    treating the given prior_filename as an image representing the prior,
    and computing a new modern coordinate pair as the MAP of the posterior
    resulting, all using grid approximation."""
    prior = ImagePrior(prior_filename, (35,5), (65,95), res)
    places = pd.read_csv(data_file, encoding='cp1252')
    places.rename(columns={
        'modern_lat': 'original_lat',
        'modern_lon': 'original_lon'}, inplace=True)
    known = places[places.disposition == 'known']
    known.is_copy = False
    known.ix[:, 'modern_lat'] = known.ix[:, 'original_lat']
    known.ix[:, 'modern_lon'] = known.ix[:, 'original_lon']
    unknown = places[places.disposition == 'unknown']
    unknown.is_copy = False
    adjusted = unknown.apply(prior.bayesian_adjust, axis=1)
    unknown = unknown.merge(adjusted, left_index=True, right_index=True)
    kml_filename = os.path.join(PTOL_HOME, 'Data', output_base+'.kml')
    csv_filename = os.path.join(PTOL_HOME, 'Data', output_base+'.csv')
    common.write_kml_file(kml_filename, None, known, unknown)
    common.write_csv_file(csv_filename, known, unknown)

parser = argparse.ArgumentParser(description=DESCRIPTION)
parser.add_argument('--prior', required=True,
                    help='an image file representing the prior')
parser.add_argument('--data', required=True,
                    help='an data file output by one of the modules')
parser.add_argument('--output', required=True,
                    help='the base for the output kml and csv')
parser.add_argument('--resolution', default=720, type=int,
                    help='resolution for the grid approximation')
                    
if __name__ == '__main__':
    args = parser.parse_args()
    bayesian_adjust_file(args.prior,
                         os.path.join(PTOL_HOME, 'Data', args.data),
                         args.output, args.resolution)
