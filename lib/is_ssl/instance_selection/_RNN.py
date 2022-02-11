#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    RNN.py
# @Author:      Daniel Puente Ramírez
# @Time:        22/11/21 08:22

from collections import deque

import numpy as np
import pandas as pd

from ._CNN import CNN
from .utils import transform


class RNN:

    def __init__(self):
      self.x_attr = None

    def filter(self, X, y):
        """
        Implementation of The Reduced Nearest Neighbor

        RNN is an extension of CNN. Firstly CNN will be executed in order to have
        S-CCN. It will perform iterative sample removal from S, and reclasificate
        all T, in hopes that there is no sample inside T classified incorrectly,
        in case there is at least one, the sample removed will be added again to S.

        :param X: dataset with scikit-learn structure.
        :return: the input dataset with the remaining samples.
        """
        self.x_attr = X.keys()
        cnn = CNN()
        X, y = cnn.filter(X,y)
        S = transform(X, y)

        data = deque([x for x in S['data']])
        target = deque([x for x in S['target']])

        for index, instance in enumerate(zip(S.data, S.target)):
            (sample, class_sample) = instance
            data.popleft()
            target.popleft()

            for x_class, x_sample in zip(S['target'], S['data']):
                euc = []
                for s_sample in data:
                    euc.append(np.linalg.norm(s_sample - x_sample))
                euc = np.array(euc)
                euc_nn = np.amin(euc)
                index_nn = np.ravel(np.where(euc == euc_nn))
                nn_class = target[index_nn[0]]

                if nn_class != x_class:
                    data.append(sample)
                    target.append(class_sample)
                    break

        X = pd.DataFrame(data, columns=self.x_attr)
        y = pd.DataFrame(target)

        return X, y
