#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    DROP3.py
# @Author:      Daniel Puente Ramírez
# @Time:        31/12/21 16:00
# @Version:     3.0

import copy
from sys import maxsize

import numpy as np
from sklearn.neighbors import NearestNeighbors
from tqdm import trange


def with_without(x_sample, samples_info):
    with_ = 0
    without = 0
    x_associates = samples_info[x_sample][1]
    associates_targets = [samples_info[tuple(x)][2] for x in x_associates]
    associates_neighs = [samples_info[tuple(x)][0] for x in x_associates]

    for a_associate, a_target, a_neighs in zip(x_associates,
                                               associates_targets,
                                               associates_neighs):

        neighs_targets = [samples_info[tuple(x)][2] for x in a_neighs]

        # With
        count = np.bincount(neighs_targets[:-1])
        max_class = np.where(count == np.amax(count))[0][0]
        if max_class == a_target:
            with_ += 1

        # Without
        for index_a, neigh in enumerate(a_neighs):
            if np.array_equal(neigh, x_sample):
                break
        count = np.bincount(neighs_targets[:index_a] + neighs_targets[
                                                       index_a + 1:])
        max_class = np.where(count == np.amax(count))[0][0]
        if max_class == a_target:
            without += 1

    return with_, without


def DROP3(X, k):
    """
    Implementation of DROP3.

    The Decremental Reduction Optimization Procedure (DROP) algorithms base
    their selection rule in terms of the partner and associate concept.
    At the very beginning a Wilson Editing algorithm is performed in order to
    remove any noise that may ve contained in the data. Followed by the DROP
    algorithm, in which an instance will be removed is its associates are
    correctly classified without the instance.

    :param X: dataset with scikit-learn structure.
    :param k: int: number of neighbors to evaluate.
    :return: the input dataset with the remaining samples.
    """

    S = copy.deepcopy(X)
    initial_samples = S['data']
    initial_targets = S['target']

    initial_samples, samples_index = np.unique(ar=initial_samples,
                                               return_index=True, axis=0)
    initial_targets = initial_targets[samples_index]

    knn = NearestNeighbors(n_neighbors=k + 2, n_jobs=-1, p=2)
    knn.fit(initial_samples)

    # Samples_info -> dict{x_sample : list([list(k+1-NN), list(x_associates),
    # label])}
    samples_info = {tuple(x): [[], [], y] for x, y in zip(initial_samples,
                                                          initial_targets)}

    initial_distances = []

    for x_sample, x_target in zip(initial_samples, initial_targets):
        # Find distance to closest enemy
        min_distance = maxsize
        for y_sample, y_label in zip(initial_samples, initial_targets):
            if x_target != y_label:
                xy_distance = np.linalg.norm(x_sample - y_sample)
                if xy_distance < min_distance:
                    min_distance = xy_distance
        initial_distances.append([x_sample, x_target, min_distance])

        # Find k+1-NN
        _, neigh_ind = knn.kneighbors([x_sample])
        x_neighs = [initial_samples[x] for x in neigh_ind[0][1:]]
        samples_info[tuple(x_sample)][0] = x_neighs

        # Add x in the associates lists of x_neighs
        for neigh in x_neighs[:-1]:
            samples_info[tuple(neigh)][1].append(x_sample)

    initial_distances.sort(key=lambda x: x[2], reverse=True)

    removed = 0
    size = len(initial_distances)
    for index_x in trange(size):
        x_sample = initial_distances[index_x - removed][0]

        with_, without = with_without(tuple(x_sample), samples_info)

        if without >= with_:
            initial_distances = initial_distances[:index_x - removed] + \
                                initial_distances[index_x - removed + 1:]
            removed += 1

            # For each associate of x_sample
            for a_associate_of_x in samples_info[(tuple(x_sample))][1]:
                # a_associate_of_x = a_associate_of_x.tolist()
                # Remove x_sample from a_associate neighs
                a_neighs = samples_info[tuple(a_associate_of_x)][0]
                for index_a, neigh in enumerate(a_neighs):
                    if np.array_equal(neigh, x_sample):
                        break
                a_neighs = a_neighs[:index_a] + a_neighs[index_a + 1:]
                try:
                    assert len(a_neighs) == k
                except AssertionError:
                    breakpoint()
                # Find a new neigh for the associate
                remaining_samples = [x for x, _, _ in initial_distances]
                knn = NearestNeighbors(n_neighbors=k + 2, n_jobs=-1, p=2)
                knn.fit(remaining_samples)
                _, neigh_ind = knn.kneighbors([a_associate_of_x])
                possible_neighs = [initial_distances[x][0] for x in
                                   neigh_ind[0]]

                for pos_neigh in possible_neighs[1:]:
                    was_in = False
                    for old_neigh in a_neighs:
                        if np.array_equal(old_neigh, pos_neigh):
                            was_in = True
                            break
                    if not was_in:
                        a_neighs.append(pos_neigh)
                        break

                try:
                    assert len(a_neighs) == k + 1
                except AssertionError:
                    print('Duplicated instances')
                    breakpoint()

                samples_info[tuple(a_associate_of_x)][0] = a_neighs

                # Add a_associate to the associates list of the new neigh
                new_neigh = a_neighs[-1]
                try:
                    samples_info[tuple(new_neigh)][1].append(a_associate_of_x)
                except TypeError:
                    breakpoint()

    S['data'] = np.array([x for x, _, _ in initial_distances])
    S['target'] = np.array([x for _, x, _ in initial_distances])

    return S
