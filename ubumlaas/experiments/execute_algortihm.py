from abc import ABC, abstractmethod
import sklearn
import sklearn.base
import sklearn.cluster
import sklearn.linear_model
import sklearn.metrics
import sklearn.ensemble
import sklearn.neighbors
import sklearn.model_selection
import sklearn.preprocessing
import sklearn.multiclass
from sklearn.model_selection import KFold

from ubumlaas import create_app
import pandas as pd
import variables as v
import traceback
import pickle

from ubumlaas.utils import send_email
from time import time
import json
import os
import numpy as np

import weka.core.jvm as jvm
from weka.classifiers import Classifier
from weka.core.classes import Random
from weka.classifiers import Evaluation
from weka.core.converters import Loader
import weka.core.serialization as serialization
from ubumlaas.util import get_dataframe_from_file

import tempfile
import shutil

class AbstractExecute(ABC):

    @abstractmethod
    def create_model(self, algorithm_name, algorithm_configuration):
        pass
    @abstractmethod
    def serialize(self, model, path):
        pass
    @abstractmethod
    def deserialize(self, path):
        pass
    @abstractmethod
    def train(self, X, y):
        pass
    @abstractmethod
    def predict(self, model, X):
        pass
    @abstractmethod
    def predict_proba(self, model, X):
        pass
    @abstractmethod
    def generate_train_test_split(self, X, y, train_size):
        if train_size == 100:
            return X, y, [], []

        return sklearn.model_selection. \
            train_test_split(X, y, train_size=train_size/100)
        
    @abstractmethod
    def generate_KFolds(self, X, y, n_splits=3, shuffle=False, random_state=None): 
        folds=[] 
        kf = KFold(n_splits=n_splits, shuffle=shuffle, random_state=random_state) 
        for train_index, test_index in kf.split(X): 
            X_train, X_test = X[train_index], X[test_index] 
            y_train, y_test = y[train_index], y[test_index] 
            folds.append((X_train, X_test, y_train, y_test)) 
        return folds 
 


class Execute_sklearn(AbstractExecute):


    def create_model(self, algorithm_name, algorithm_configuration, ):
        return eval(algorithm_name+"(**algorithm_configuration)")
   
    def serialize(self, model, path):
        pickle.dump(model, open(path, 'wb'))
 
    def deserialize(self, path):
        return pickle.load(open(path,'rb'))

    def train(self,model, X, y):
        model.fit(X, y)

    def predict(self, model, X):
        return model.predict(X)

    def predict_proba(self, model, X):
        model.predict_proba(X)

    def generate_train_test_split(self, X, y, train_size):
        return super().generate_train_test_split( X, y, train_size)

    def generate_KFolds(self, X, y, n_splits=3, shuffle=False, random_state=None): 
        return super().generate_KFolds( X, y, n_splits, shuffle, random_state) 

class Execute_weka(AbstractExecute):

    def create_weka_dataset(self, X, y, y_uniques=None):
    """Create weka dataset using temporaly file

    Arguments:
        X {array like} -- non target class instances
        y {array like} -- target class instances

    Returns:
        java object wrapped -- weka dataset
    """
    try:
        # Create new temporal file
        temp = tempfile.NamedTemporaryFile()

        # Concat X and y. Write csv to temporaly file.
        X_df = pd.DataFrame(X)
        y_df = pd.DataFrame(y)
        dataframe = pd.concat([X_df, y_df], axis=1)
        dataframe.to_csv(temp.name, index=None)

        if y_uniques is not None:
            options = ["-L", "{}:{}".format(dataframe.shape[1],
                                ",".join(map(str, y_uniques)))]
        loader = Loader(classname="weka.core.converters.CSVLoader",
                        options = options)
        data = loader.load_file(temp.name)
        # Last column of data is target
        data.class_is_last()
    finally:
        temp.close()
    return data

    def create_model(self, algorithm_name, algorithm_configuration, configuration):
        lincom = []

        for i in algorithm_configuration.keys():
            v = algorithm_configuration[i]
            if v is not False:
                lincom.append(configuration[i]["command"])
            if not isinstance(v, bool):
                lincom.append(str(v))
        return Classifier(classname=algorithm_name, options=lincom)
   
    def serialize(self, model, path):
        serialization.write(path, model)
 
    def deserialize(self, path):
        return Classifier(jobject=serialization.read(path))

    def train(self, model, X, y, is_classification=False):
        y_unique=None
        if classification:
            y_unique = list(set(y))
            y_unique.sort()
        data = self.create_weka_dataset(X, y, y_unique)
        model.build_classifier(data)
        

    def predict(self, model, X, y):
        pass

    def predict_proba(self, model, X, y):
        pass

    def generate_train_test_split(self, X, y, train_size):
        return super().generate_train_test_split( X, y, train_size)

    def generate_KFolds(self, X, y, n_splits=3, shuffle=False, random_state=None): 
        return super().generate_KFolds(X, y, n_splits, shuffle, random_state)