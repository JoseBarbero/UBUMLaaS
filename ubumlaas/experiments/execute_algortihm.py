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
from sklearn.model_selection import StratifiedKFold, KFold

import pandas as pd
import pickle

import json

import weka.core.jvm as jvm
from weka.classifiers import Classifier
from weka.core.converters import Loader
import weka.core.serialization as serialization
from ubumlaas.util import get_dataframe_from_file

from lib.skmultilearn.ext import Meka

import tempfile



class AbstractExecute(ABC):

    @abstractmethod
    def create_model(self):
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

    def kfold_algorithm(self):
        if self.is_classification():
            return "StratifiedKFold"
        else:
            return "KFold"

    def open_dataset(self, path, filename, columns, target):
        data = get_dataframe_from_file(path, filename)
        X = data.loc[:, columns]
        y = data[target]
        return X, y

    def close(self):
        pass

    def find_y_uniques(self, y):
        pass

    def generate_train_test_split(self, X, y, train_size):
        if train_size == 100:
            return X, [], y, []

        return sklearn.model_selection. \
            train_test_split(X, y, train_size=train_size/100)

    def generate_KFolds(self, X, y, n_splits=3, shuffle=False,
                        random_state=None):
        folds = []

        kf = eval(self.kfold_algorithm()+"(n_splits=n_splits, shuffle=shuffle, \
                             random_state=random_state)")

        for train_index, test_index in kf.split(X, y):

            X_train, X_test = X.iloc[train_index, :], \
                              X.iloc[test_index, :]
            if len(y.shape) == 1:
                y_train, y_test = y.iloc[train_index], y.iloc[test_index]
            else:
                y_train, y_test = y.iloc[train_index, :], y.iloc[test_index, :]
            folds.append((X_train, X_test, y_train, y_test))
        return folds

    def _know_type(self, exp):
        if exp["alg"]["alg_typ"] == "Mixed":
            from ubumlaas.models import get_algorithm_by_name
            config = json.loads(exp["alg_config"])
            for c in config:
                if type(config[c]) == dict:
                    new_exp = {"alg": get_algorithm_by_name(
                                        config[c]["alg_name"]
                                      ).to_dict(),
                               "alg_config": config[c]["parameters"]}
                    return self._know_type(new_exp)
        return exp["alg"]["alg_typ"]


class Execute_sklearn(AbstractExecute):

    def __init__(self, experiment):
        self.algorithm_name = experiment["alg"]["alg_name"]  # example weka.classification.trees.J48
        self.algorithm_type = super()._know_type(experiment)  # classification, reggression or mixed
        self.algorithm_configuration = json.loads(experiment["alg_config"])  # configuration algorithm
        self.configuration = json.loads(experiment["alg"]["config"])
        self.experiment_configuration = json.loads(experiment["exp_config"])

    def __create_sklearn_model(self, alg_name, alg_config):
        """Create a sklearn model recursive

        Arguments:
            alg_name {string} -- sklearn model name
            alg_config {dict} -- parameters
        """
        for ac in alg_config:
            if type(alg_config[ac]) == dict:
                alg_config[ac] = self.__create_sklearn_model(
                                        alg_config[ac]["alg_name"],
                                        alg_config[ac]["parameters"])

        model = eval(alg_name+"(**alg_config)")
        return model

    def create_model(self):
        return self.__create_sklearn_model(self.algorithm_name,
                                           self.algorithm_configuration)

    def serialize(self, model, path):
        pickle.dump(model, open(path, 'wb'))

    def deserialize(self, path):
        return pickle.load(open(path, 'rb'))

    def train(self, model, X, y):
        model.fit(X, y)

    def predict(self, model, X, y):
        predictions = model.predict(X)
        y_score = None
        if self.is_classification():
            y_score = model.predict_proba(X)
        return predictions, y_score

    def open_dataset(self, path, filename):
        return super().open_dataset(path, filename,
                                    self.experiment_configuration["columns"],
                                    self.experiment_configuration["target"])

    def generate_train_test_split(self, X, y, train_size):
        return super().generate_train_test_split(X, y, train_size)

    def generate_KFolds(self, X, y, n_splits=3,
                        shuffle=False, random_state=None):
        return super().generate_KFolds(X, y, n_splits, shuffle, random_state)

    def is_classification(self):
        return self.algorithm_type == "Classification"

    def close(self):
        pass

    def find_y_uniques(self, y):
        pass


class Execute_weka(AbstractExecute):

    def __init__(self, experiment):
        jvm.start(packages=True)
        self.algorithm_name = experiment["alg"]["alg_name"]  # for example: weka.classification.trees.J48
        self.algorithm_type = super()._know_type(experiment)  # classification, reggression or mixed
        self.algorithm_configuration = json.loads(experiment["alg_config"])  # configuration algorithm
        self.configuration = json.loads(experiment["alg"]["config"])
        self.experiment_configuration = json.loads(experiment["exp_config"])

        self.y_uniques = None

    def create_weka_dataset(self, X, y):
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
            options = None
            if self.y_uniques is not None:
                options = ["-L", "{}:{}".format(dataframe.shape[1],
                           ",".join(map(str, self.y_uniques)))]
            loader = Loader(classname="weka.core.converters.CSVLoader",
                            options=options)
            data = loader.load_file(temp.name)
            # Last column of data is target
            data.class_is_last()
        finally:
            temp.close()
        return data

    def create_weka_parameters(alg_name, alg_config, baseconf=None):

        if baseconf is None:
            from ubumlaas.models import get_algorithm_by_name
            exp = get_algorithm_by_name(alg_name)
            baseconf = json.loads(exp.config)

        lincom = []
        for i in alg_config:
            parameter = alg_config[i]
            if type(parameter) == dict:
                sub_list = Execute_weka.\
                    create_weka_parameters(parameter["alg_name"],
                                           parameter["parameters"])
                lincom += [baseconf[i]["command"], parameter["alg_name"], "--"]
                lincom += sub_list
            else:
                if parameter is not False:
                    lincom.append(baseconf[i]["command"])
                if not isinstance(parameter, bool):
                    lincom.append(str(parameter))

        return lincom

    def create_model(self):
        lincom = Execute_weka.\
            create_weka_parameters(self.algorithm_name,
                                   self.algorithm_configuration,
                                   self.configuration)
        return Classifier(classname=self.algorithm_name, options=lincom)

    def serialize(self, model, path):
        serialization.write(path, model)

    def deserialize(self, path):
        return Classifier(jobject=serialization.read(path))

    def train(self, model, X, y):
        data = self.create_weka_dataset(X, y)
        model.build_classifier(data)

    def predict(self, model, X, y):
        if y is None:
            # TODO multi-label is different
            y = pd.DataFrame({
                    self.experiment_configuration["target"]: ["?"]*len(X.index)
                })

        data_test = self.create_weka_dataset(X, y)
        y_score = None
        if self.is_classification():
            y_pred = [data_test.class_attribute.value(
                            int(model.classify_instance(instance))
                        )for instance in data_test
                      ]
            y_score = model.distributions_for_instances(data_test)
        else:
            y_pred = [model.classify_instance(instance)
                      for instance in data_test
                      ]

        try:  # Trying to convert to int
            y_pred = [int(pred) for pred in y_pred]
        except ValueError:
            pass
        return y_pred, y_score

    def open_dataset(self, path, filename):
        return super().open_dataset(path, filename,
                                    self.experiment_configuration["columns"],
                                    self.experiment_configuration["target"])

    def generate_train_test_split(self, X, y, train_size):
        return super().generate_train_test_split(X, y, train_size)

    def generate_KFolds(self, X, y, n_splits=3,
                        shuffle=False, random_state=None):
        return super().generate_KFolds(X, y, n_splits, shuffle, random_state)

    def is_classification(self):
        return self.algorithm_type == "Classification"

    def close(self):
        jvm.stop()

    def find_y_uniques(self, y):
        if self.is_classification():
            uniques = y.unique()
            uniques.sort()
            self.y_uniques = uniques


class Execute_meka(AbstractExecute):

    def __init__(self, experiment):
        self.algorithm_name = experiment["alg"]["alg_name"]  # example weka.classification.trees.J48
        self.algorithm_type = super()._know_type(experiment)  # classification, reggression or mixed
        self.algorithm_configuration = json.loads(experiment["alg_config"])  # configuration algorithm
        self.configuration = json.loads(experiment["alg"]["config"])
        self.experiment_configuration = json.loads(experiment["exp_config"])

    def kfold_algorithm(self):
        return "KFold"

    def create_model(self):
        meka_classifier, weka_classifier = self._get_options()
        model = Meka(
            meka_classifier=meka_classifier,
            weka_classifier=weka_classifier
        )
        return model

    def _get_options(self):
        meka_classifier = self.algorithm_name
        weka_classifier = ""
        parameters = Execute_weka.create_weka_parameters(self.algorithm_name, self.algorithm_configuration)
        while len(parameters) > 0:
            p = parameters.pop(0)
            if p == "-W":
                break
            meka_classifier += (" " + p)

        for p in parameters:
            weka_classifier += (p + " ")
        weka_classifier = weka_classifier.strip()
        return meka_classifier, weka_classifier

    def serialize(self, model, path):
        pickle.dump(model, open(path, 'wb'))

    def deserialize(self, path):
        return pickle.load(open(path, 'rb'))

    def train(self, model, X, y):
        model.fit(X.values, y.values)

    def predict(self, model, X, y):
        predictions = model.predict(X.values, y.values)
        predictions = pd.DataFrame(predictions.toarray())
        predictions.columns = y.columns
        y_score = None
        return predictions, y_score

    def is_classification(self):
        return self.algorithm_type == "MultiClassification"

    def open_dataset(self, path, filename):
        return super().open_dataset(path, filename,
                                    self.experiment_configuration["columns"],
                                    self.experiment_configuration["target"])
