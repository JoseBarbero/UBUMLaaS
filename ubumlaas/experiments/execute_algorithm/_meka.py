import sklearn
import sklearn.base
import sklearn.cluster
import sklearn.mixture
import sklearn.linear_model
import sklearn.metrics
import sklearn.ensemble
import sklearn.neighbors
import sklearn.model_selection
import sklearn.preprocessing
import sklearn.multiclass

from sklearn.model_selection import KFold

import pickle

from lib.skmultilearn.ext import Meka

from ubumlaas.experiments.execute_algorithm import Abstract_execute
from ubumlaas.experiments.execute_algorithm._weka import Execute_weka

import variables as v


class Execute_meka(Abstract_execute):

    def __init__(self, experiment):
        """Initizialice attributes from experiment dict

        Arguments:
            experiment {dict} -- experiment dictionary
        """
        Abstract_execute.__init__(self, experiment)
        v.app.logger.info("Execution library - %d - MEKA", self.id)

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
        v.app.logger.info("Model saved - %d - %s", self.id, self.algorithm_name)

    def load_meka_model(self, path):
        """Load Meka java object
        
        Arguments:
            path {str} -- path where saves the model
        
        Returns:
            [java object] -- Meka model trained
        """
        with open(path, 'rb') as fp:
            meka_model = fp.read()
        v.app.logger.info("Model readed - %d - %s", self.id, self.algorithm_name)    
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
        v.app.logger.info("Training model - %d - %s", self.id, self.algorithm_name)
        model.fit(X.values, y.values)
        v.app.logger.info("Model trained - %d - %s", self.id, self.algorithm_name)

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
