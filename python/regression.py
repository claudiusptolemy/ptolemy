# regression.py: Predict modern coordinates for places
# described by Ptolemy using linear regression against
# the places that have been suggested by other means.

import os
import sys

import numpy as np
from sklearn.linear_model import LinearRegression

NF = range(2)

class Regression(object):

    def fit(self, X, y):
        self.m = [LinearRegression() for i in NF]
        for i in NF:
            self.m[i].fit(X, y.ix[:,i])

    def predict(self, X):
        y = np.zeros((len(X),2))
        for i in NF:
            y[:,i] = self.m[i].predict(X)
        return y
