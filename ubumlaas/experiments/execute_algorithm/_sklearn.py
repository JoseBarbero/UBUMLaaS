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

import pickle

from ubumlaas.experiments.execute_algorithm import Abstract_execute


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
        return Execute_sklearn\
            .__create_sklearn_model(self.algorithm_name,
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
        if y is None:
            model.fit(X)
        else:
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
