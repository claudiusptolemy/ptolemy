# regression.py: Predict modern coordinates for places
# described by Ptolemy using linear regression against
# the places that have been suggested by other means.

import os
import sys

import numpy as np
from sklearn.linear_model import LinearRegression

NF = range(2)


class Regression(object):

    def __init__(self):
        self.m = None

    def fit(self, x, y):
        self.m = [LinearRegression() for _ in NF]
        for i in NF:
            self.m[i].fit(x, y.ix[:, i])

    def predict(self, x):
        y = np.zeros((len(x), 2))
        for i in NF:
            y[:, i] = self.m[i].predict(x)
        return y
