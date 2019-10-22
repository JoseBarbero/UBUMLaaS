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
import numpy as np
import json

import weka.core.jvm as jvm
from weka.classifiers import Classifier
from weka.core.converters import Loader
import weka.core.serialization as serialization
from ubumlaas.util import get_dataframe_from_file

from lib.skmultilearn.ext import Meka

import tempfile



class Abstract_execute(ABC):

    def __init__(self, experiment):
        """Initizialice attributes from experiment dict
        
        Arguments:
            experiment {dict} -- experiment dictionary
        """
        self.algorithm_name = experiment["alg"]["alg_name"]  # for example: weka.classification.trees.J48
        self.algorithm_type = Abstract_execute._know_type(experiment)  # classification, reggression or mixed
        self.algorithm_configuration = json.loads(experiment["alg_config"])  # configuration algorithm
        self.configuration = json.loads(experiment["alg"]["config"])
        self.experiment_configuration = json.loads(experiment["exp_config"])


    @abstractmethod
    def create_model(self):
        """Create the model with experiment
        
        Returns:
            [object] -- model with the experiment configuration
        """
        return None

    @abstractmethod
    def serialize(self, model, path):
        """Serialize the model in specific path
        
        
        Arguments:
            model {object} -- the model to serialize
            path {str} -- path to save the model serialized
        """
        pass

    @abstractmethod
    def deserialize(self, path):
        """Deserialize the model in the specific path
        
        Arguments:
            path {str} -- path with the model file saved
        
        Returns:
            [object] -- model deserialized
        """
        return None

    @abstractmethod
    def train(self, model, X, y):
        """Train the model with attributes columns (X) and targets columns (Y)
        
        Arguments:
            model {object} -- model to train
            X {DataFrame} -- attributes columns
            y {FataFrame} -- targets columns
        """
        pass

    @abstractmethod
    def predict(self, model, X):
        """Predict with X columns values using the model
        
        Arguments:
            model {object} -- model to use for predictions
            X {DataFrame} -- dataframe with X columns values
        
        Returns:
            list, list -- predictions values, distribution class if is classified or None otherwise
        """
        return None, None

    def kfold_algorithm(self):
        """Return KFold algorithm if is classification or not
        
        Returns:
            [func] -- StratifiedKafold if is classification or KFold in other case
        """
        if self.is_classification():
            return StratifiedKFold
        else:
            return KFold

    def open_dataset(self, path, filename):
        """Open dataset file and return as X and y
        
        Arguments:
            path {str} -- path without file nanme
            filename {str} -- file name to open
        
        Returns:
            DataFrame, DataFrame -- X and Y DataFrame
        """
        data = get_dataframe_from_file(path, filename)
        X = data.loc[:, self.experiment_configuration["columns"]]
        y = None
        if set(self.experiment_configuration["target"]) <= set(data.columns):
            y = data.loc[:, self.experiment_configuration["target"]]
        return X, y

    def close(self):
        """Close resources used in the algorithm
        """
        pass

    def find_y_uniques(self, y):
        """Find unique values in target
        
        Arguments:
            y {DataFrame} -- target column
        """
        pass

    def generate_train_test_split(self, X, y, train_size):
        """Generate train test split
        
        Arguments:
            X {DataFrame} -- attributes columns
            y {DataFrame} -- targets columns
            train_size {int} -- train size between 1 and 100
        
        Returns:
            [DataFrames] -- X_train, X_test, y_train, y_test
        """
        if train_size == 100:
            return X, [], y, []

        return sklearn.model_selection. \
            train_test_split(X, y, train_size=train_size/100)

    def generate_KFolds(self, X, y, n_splits=3, shuffle=False,
                        random_state=None):
        """Generate KFolds
        
        Arguments:
            X {DataFrame} -- Attribute columns
            y {DataFrame} -- Target columns
        
        Keyword Arguments:
            n_splits {int} -- Number of folds. Must be at least 2. (default: {3})
            shuffle {bool} -- Whether to shuffle the data before splitting into batches. (default: {False})
            random_state {int, RandomState instance or None} -- If int, random_state is the seed used by the random number generator; If RandomState instance, random_state is the random number generator; If None, the random number generator is the RandomState instance used by np.random. Used when shuffle == True. (default: {None})
        
        Returns:
            [list] -- list of tuples with X_train, X_test, y_train, y_test in each tuple
        """
        folds = []

        kf = self.kfold_algorithm()(n_splits=n_splits, shuffle=shuffle, random_state=random_state)

        for train_index, test_index in kf.split(X, y):

            X_train, X_test = X.iloc[train_index, :], \
                              X.iloc[test_index, :]
        
            y_train, y_test = y.iloc[train_index, :], y.iloc[test_index, :]
            folds.append((X_train, X_test, y_train, y_test))
        return folds

    @staticmethod
    def _know_type(exp):
        """If the algorthim is mixed, find the deepest base classifier
        
        Arguments:
            exp {dict} -- experiment dict
        
        Returns:
            [str] -- 
        """
        if exp["alg"]["alg_typ"] == "Mixed":
            from ubumlaas.models import get_algorithm_by_name
            config = json.loads(exp["alg_config"])
            for c in config:
                if type(config[c]) == dict:
                    new_exp = {"alg": get_algorithm_by_name(
                                        config[c]["alg_name"]
                                      ).to_dict(),
                               "alg_config": config[c]["parameters"]}
                    return Abstract_execute._know_type(new_exp)
        return exp["alg"]["alg_typ"]

    def is_classification(self):
        """Check if the algorithm type is Classification
        
        Returns:
            [bool] -- True if algorithm is Classfication
        """
        return self.algorithm_type == "Classification"

class Execute_sklearn(Abstract_execute):
    
    def __init__(self, experiment):
        """Initizialice attributes from experiment dict
        
        Arguments:
            experiment {dict} -- experiment dictionary
        """
        Abstract_execute.__init__(self, experiment)

    @staticmethod
    def __create_sklearn_model(alg_name, alg_config):
        """Create a sklearn model recursive

        Arguments:
            alg_name {string} -- sklearn model name
            alg_config {dict} -- parameters
        """
        for ac in alg_config:
            if type(alg_config[ac]) == dict:
                alg_config[ac] = Execute_sklearn.__create_sklearn_model(
                                        alg_config[ac]["alg_name"],
                                        alg_config[ac]["parameters"])

        model = eval(alg_name+"(**alg_config)")
        return model

    def create_model(self):
        """Create the model with experiment
        
        Returns:
            [object] -- model with the experiment configuration
        """
        return Execute_sklearn.__create_sklearn_model(self.algorithm_name,
                                           self.algorithm_configuration)

    def serialize(self, model, path):
        """Serialize the model in specific path
        
        
        Arguments:
            model {object} -- the model to serialize
            path {str} -- path to save the model serialized
        """
        pickle.dump(model, open(path, 'wb'))

    def deserialize(self, path):
        """Deserialize the model in the specific path
        
        Arguments:
            path {str} -- path with the model file saved
        
        Returns:
            [object] -- model deserialized
        """
        return pickle.load(open(path, 'rb'))

    def train(self, model, X, y):
        """Train the model with attributes columns (X) and targets columns (Y)
        
        Arguments:
            model {object} -- model to train
            X {DataFrame} -- attributes columns
            y {FataFrame} -- targets columns
        """
        model.fit(X, y.values.ravel())

    def predict(self, model, X):
        """Predict with X columns values using the model
        
        Arguments:
            model {object} -- model to use for predictions
            X {DataFrame} -- dataframe with X columns values
        
        Returns:
            list, list -- predictions values, distribution class if is classified or None otherwise
        """
        predictions = model.predict(X)
        y_score = None
        if self.is_classification():
            y_score = model.predict_proba(X)
        return predictions, y_score

class Execute_weka(Abstract_execute):

    def __init__(self, experiment):
        """Initizialice attributes from experiment dict and starts Java Virtual Machine
        
        Arguments:
            experiment {dict} -- experiment dictionary
        """
        Abstract_execute.__init__(self, experiment)

        jvm.start(packages=True)
        self.y_uniques = None

    def create_weka_dataset(self, X, y = None):
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
            
            if y is None:
                y = pd.DataFrame(["?"]*X.shape[0], columns= self.experiment_configuration["target"])
            X.reset_index(drop=True, inplace=True)
            y.reset_index(drop=True, inplace=True)
            dataframe = pd.concat([X, y], axis=1, ignore_index=True)
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

    @staticmethod
    def create_weka_parameters(alg_name, alg_config, baseconf=None):
        """Create weka command line parameter based in the algorithm name and algorithm configuration
        
        Arguments:
            alg_name {str} -- algortihm name, for example: weka.classifiers.trees.J48
            alg_config {dict} -- algorithm configuration
        
        Keyword Arguments:
            baseconf {dict} -- base configuration of the algortihm configuration (default: {None})
        
        Returns:
            [list] -- list of the command line parameter
        """
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
        """Create the model with experiment
        
        Returns:
            [java object] -- model with the experiment configuration
        """
        lincom = Execute_weka.\
            create_weka_parameters(self.algorithm_name,
                                   self.algorithm_configuration,
                                   self.configuration)
        return Classifier(classname=self.algorithm_name, options=lincom)

    def serialize(self, model, path):
        """Serialize the java model in specific path
        
        
        Arguments:
            model {java object} -- the model to serialize
            path {str} -- path to save the model serialized
        """
        serialization.write(path, model)

    def deserialize(self, path):
        """Deserialize the model in the specific path
        
        Arguments:
            path {str} -- path with the model file saved
        
        Returns:
            [java object] -- model deserialized
        """
        return Classifier(jobject=serialization.read(path))

    def train(self, model, X, y):
        """Train the model with attributes columns (X) and targets columns (Y)
        
        Arguments:
            model {object} -- model to train
            X {DataFrame} -- attributes columns
            y {Series} -- target column
        """
        data = self.create_weka_dataset(X, y)
        model.build_classifier(data)

    def predict(self, model, X):
        """Predict with X columns values using the model
        
        Arguments:
            model {object} -- model to use for predictions
            X {DataFrame} -- dataframe with X columns values
        
        Returns:
            list, list -- predictions values, distribution class if is classified or None otherwise
        """
        data_test = self.create_weka_dataset(X)
        y_score = None
        if self.is_classification():
            y_pred = [data_test.class_attribute.value(
                            int(model.classify_instance(instance))
                        )for instance in data_test
                      ]
            y_score = model.distributions_for_instances(data_test)
            try: #Trying to convert to int
                y_pred = [float(pred) for pred in y_pred]
            except ValueError:
                pass
        else:
            y_pred = [model.classify_instance(instance)
                      for instance in data_test
                      ]
        return y_pred, y_score
        
    def close(self):
        """Closes Java Virtual Machine
        """
        jvm.stop()

    def find_y_uniques(self, y):
        """If the algorithm is classification, finds uniques nominal values
        
        Arguments:
            y {Series} -- target column
        """
        if self.is_classification():
            uniques = np.unique(y.values)
            uniques.sort()
            self.y_uniques = uniques
            


class Execute_meka(Abstract_execute):

    def __init__(self, experiment):
        """Initizialice attributes from experiment dict
        
        Arguments:
            experiment {dict} -- experiment dictionary
        """
        Abstract_execute.__init__(self, experiment)

    def kfold_algorithm(self):
        """Uses KFold function
        
        Returns:
            [func] -- KFold function
        """
        return KFold

    def create_model(self):
        """Create the model with experiment
        
        Returns:
            [object] -- model with the experiment configuration
        """
        meka_classifier, weka_classifier = self._get_options()
        model = Meka(
            meka_classifier=meka_classifier,
            weka_classifier=weka_classifier
        )
        return model

    def _get_options(self):
        """Return meka and weka parameters
        
        Returns:
            [str, str] -- meka classifier and it options parameter, weka classifier and it options
        """
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

    def save_meka_model(self, model, path):
        """Saves the meka model
        
        Arguments:
            model {object} -- skmultilearn Meka
            path {str} -- path where saves the model
        """
        with open(path, 'wb') as fp:
            fp.write(model.classifier_dump)

    def load_meka_model(self, path):
        """Load Meka java object
        
        Arguments:
            path {str} -- path where saves the model
        
        Returns:
            [java object] -- Meka model trained
        """
        with open(path, 'rb') as fp:
            meka_model = fp.read()
        return meka_model

    def serialize(self, model, path):
        """Serialize skmultilean model and java object
        
        Arguments:
            model {object} -- skmultilearn object
            path {str} -- path
        """
        pickle.dump(model, open(path + "skmultilearn.model", 'wb'))
        self.save_meka_model(model, path)

    def deserialize(self, path):
        """Deserialize skmultilearn object
        
        Arguments:
            path {str} -- path
        
        Returns:
            [object] -- skmultilearn Meka
        """
        return pickle.load(open(path + "skmultilearn.model", 'rb'))

    def train(self, model, X, y):
        """Train the model with attributes columns (X) and targets columns (Y)
        
        Arguments:
            model {object} -- model to train
            X {DataFrame} -- attributes columns
            y {DataFrame} -- targets column
        """
        model.fit(X.values, y.values)

    def predict(self, model, X):
        """Predict with X columns values using the model
        
        Arguments:
            model {object} -- model to use for predictions
            X {DataFrame} -- dataframe with X columns values
        
        Returns:
            list, None -- predictions values, hasn't got class prediction
        """
        predictions = model.predict(X.values)
        predictions = predictions.toarray()
        y_score = None
        return predictions, y_score

    def is_classification(self):
        """Check if is MultiClassfication
        
        Returns:
            [bool] -- True if algorithm type is MultiClassfication
        """
        return self.algorithm_type == "MultiClassification"
