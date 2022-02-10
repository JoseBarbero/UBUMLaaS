#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    ENN.py
# @Author:      Daniel Puente Ramírez
# @Time:        16/11/21 17:14
# @Version:     4.0

import copy

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.neighbors import NearestNeighbors
from sklearn.utils import Bunch
from .utils import transform as tr


class ENN(BaseEstimator, TransformerMixin):
    def __init__(self, nearest_neighbors=3, power_parameter=2):
      self.nearest_neighbors = nearest_neighbors
      self.power_parameter = power_parameter
      self.x_attr = None

    def fit(self, X, fit_params):
        """
        Implementation of the Wilson Editing algorithm.

        For each sample locates the *k* nearest neighbors and selects the number of
        different classes there are.
        If a sample results in a wrong classification after being classified with
        k-NN, that sample is removed from the TS.
        :param X: dataset with scikit-learn structure.
        :param k: int: number of neighbors to evaluate.
        :return: the input dataset with the remaining samples.
        """
        print('....................................................\n\n\n')
        self.x_attr = X.keys()
        X = tr(X, fit_params)
        S = copy.deepcopy(X)
        size = len(X['data'])
        s_samples = list(X['data'])
        s_targets = list(X['target'])
        removed = 0

        for index in range(size):
            x_sample = s_samples[index - removed]
            x_target = s_targets[index - removed]
            knn = NearestNeighbors(
                n_jobs=1, n_neighbors=self.nearest_neighbors, p=self.power_parameter)
            samples_not_x = s_samples[:index - removed] + s_samples[
                                                        index - removed + 1:]
            targets_not_x = s_targets[:index - removed] + s_targets[
                                                        index - removed + 1:]
            knn.fit(samples_not_x)
            _, neigh_ind = knn.kneighbors([x_sample])
            y_targets = [targets_not_x[x] for x in neigh_ind[0]]
            count = np.bincount(y_targets)
            max_class = np.where(count == np.amax(count))[0][0]
            if max_class != x_target:
                removed += 1
                s_samples = samples_not_x
                s_targets = targets_not_x

        X = pd.DataFrame(s_samples, columns=self.x_attr)
        y = pd.DataFrame(s_targets)

        return X, y
