import sklearn.naive_bayes
import sklearn.preprocessing
import sklearn.neighbors
import sklearn.preprocessing
import sklearn.tree
import sklearn.ensemble
import sklearn.model_selection
import sklearn.utils
import variables as v
import pickle
from imblearn.pipeline import make_pipeline
from ubumlaas.experiments.execute_algorithm import Abstract_execute
import lib.is_ssl.semisupervised

class Execute_ssl(Abstract_execute):
    
    def __init__(self, experiment):
        """Initizialice attributes from experiment dict

        Arguments:
            experiment {dict} -- experiment dictionary
        """
        Abstract_execute.__init__(self, experiment)
        v.app.logger.info("Execution library - %d - IS_SLL", self.id)

    @staticmethod
    def __create_model(alg_name, alg_config):
        """Create a model recursive

        Arguments:
            alg_name {string} -- model name
            alg_config {dict} -- parameters
        """
        for ac in alg_config:
            if type(alg_config[ac]) == dict:
                alg_config[ac] = Execute_ssl.__create_model(
                    alg_config[ac]["alg_name"],
                    alg_config[ac]["parameters"])

        model = eval("lib."+alg_name+"(**alg_config)")
        return model

    def create_model(self):
        """Create the model with experiment

        Returns:
            [object] -- model with the experiment configuration or pipeline if has filter
        """
        model = Execute_ssl.__create_model(
            self.algorithm_name, self.algorithm_configuration)

        if self.has_filter():
            filter = eval(self.filter_name+"(**self.filter_config)")
            return make_pipeline(filter, model)
        return model

    def serialize(self, model, path):
        """Serialize the model in specific path

        Arguments:
            model {object} -- the model to serialize
            path {str} -- path to save the model serialized
        """
        v.app.logger.info("Model saved - %d - %s",
                          self.id, self.algorithm_name)
        pickle.dump(model, open(path, 'wb'))

    def deserialize(self, path):
        """Deserialize the model in the specific path

        Arguments:
            path {str} -- path with the model file saved

        Returns:
            [object] -- model deserialized
        """
        v.app.logger.info("Model readed - %d - %s",
                          self.id, self.algorithm_name)
        return pickle.load(open(path, 'rb'))

    def train(self, model, X, y):
        """Train the model with attributes columns (X) and targets columns (Y)

        Arguments:
            model {object} -- model to train
            X {DataFrame} -- attributes columns
            y {FataFrame} -- targets columns
        """
        v.app.logger.info("Training model - %d - %s",
                          self.id, self.algorithm_name)
        
        model.fit(X, y.values.ravel())
        v.app.logger.info("Model trained - %d - %s",
                          self.id, self.algorithm_name)

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
        if self.is_semi_supervised_calssification():
            y_score = model.predict_proba(X)
        return predictions, y_score
    