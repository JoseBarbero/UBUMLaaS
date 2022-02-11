#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    ICF.py
# @Author:      Daniel Puente Ramírez
# @Time:        23/11/21 09:37
# @Version:     2.0

from sys import maxsize

import numpy as np
import pandas as pd

from ._ENN import ENN
from .utils import transform


class ICF:
    def __init__(self, nearest_neighbors=3, power_parameter=2):
      self.nearest_neighbors = nearest_neighbors
      self.power_parameter = power_parameter
      self.x_attr = None

    def __delete_multiple_element(self, list_object, indices):
        indices = sorted(indices, reverse=True)
        for idx in indices:
            if idx < len(list_object):
                list_object.pop(idx)


    def __coverage__(self, T):
        """
        Inner method that performs the coverage and reachability of T.
        :param dat: samples of T
        :param tar: target class of dat.
        :return: (cov, reachable): vectors. cov contains for each sample the
        samples that it can cover. And reachable for each sample the samples that
        are able to reach it.
        """
        size = len(T.data)
        matrix_distances = np.zeros([size, size])
        distances_to_enemies = []
        sol = []

        for sample in range(size):
            distance_to_closest_enemy = maxsize
            x_sample = T['data'][sample]
            x_target = T['target'][sample]
            for other_sample in range(size):
                y_sample = T['data'][other_sample]
                y_target = T['target'][other_sample]
                distance = np.linalg.norm(x_sample - y_sample)
                matrix_distances[sample][other_sample] = distance
                # Si son enemigas, nos quedamos con la distancia
                if x_target != y_target and distance < distance_to_closest_enemy:
                    distance_to_closest_enemy = distance
            distances_to_enemies.append(distance_to_closest_enemy)

        for sample in range(size):
            x_coverage = []
            x_target = T['target'][sample]
            distance_to_closest_enemy = distances_to_enemies[sample]
            for other_sample in range(size):
                if sample == other_sample:
                    continue
                y_target = T['target'][other_sample]
                if x_target == y_target:
                    distance_between_samples = matrix_distances[sample][
                        other_sample]
                    if distance_between_samples < distance_to_closest_enemy:
                        x_coverage.append(other_sample)
            sol.append([x_coverage])

        for sample in range(size):
            reachable = []
            x_target = T['target'][sample]
            for other_sample in range(size):
                y_target = T['target'][other_sample]
                if sample != other_sample and x_target == y_target:
                    # if x_target == y_target:
                    coverage = sol[other_sample][0]
                    if sample in coverage:
                        reachable.append(other_sample)
            sol[sample].append(reachable)

        return sol


    def filter(self, X, y):
        """
        Implementation of Iterative Case Filtering

        ICF is based on coverage and reachable, due to this two concepts it
        performs deletion of samples based on the rule: "If the reachability
        of a sample is greater than its coverage, that sample has to be removed".
        I.e. if another sample of the same class which is nearer than the closest
        enemy is able to provide more information, the sample with less coverage
        than reachable will be removed.
        Ending up with a dataset as generalized as ICF allows.
        :param X: dataset with scikit-learn structure.
        :return: the input dataset with the remaining samples.
        """
        self.x_attr = X.keys()
        enn = ENN(nearest_neighbors=self.nearest_neighbors,
                  power_parameter=self.power_parameter)
        X, y = enn.filter(X, y)
        TS = transform(X, y)

        while True:
            data = list(TS['data'])
            target = list(TS['target'])

            cov_reach = self.__coverage__(TS)

            progress = False
            removable_indexes = []
            for index in range(len(cov_reach)):
                (x_cov, x_reach) = cov_reach[index]
                if len(x_reach) > len(x_cov):
                    removable_indexes.append(index)
                    progress = True

            self. __delete_multiple_element(data, removable_indexes)
            self.__delete_multiple_element(target, removable_indexes)
            TS['data'] = data
            TS['target'] = target
            if not progress:
                break

        X = pd.DataFrame(TS['data'], columns=self.x_attr)
        y = pd.DataFrame(TS['target'])

        return X, y
