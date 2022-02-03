import sklearn.naive_bayes
import sklearn.preprocessing
import sklearn.neighbors
import sklearn.preprocessing
import sklearn.tree
import sklearn.ensemble
import sklearn.model_selection
import sklearn.utils
import variables as v
from ubumlaas.experiments.execute_algorithm import Abstract_execute

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
        """
        
        """
        pass

    def create_model(self):
        """
        
        """
        pass

    def serialize(self, model, path):
        """
        
        """
        pass

    def deserialize(self, path):
        """
        
        """
        pass

    def train(self, model, X, y):
        """
        
        """
        pass

    def predict(self, model, X):
        """
        
        """
        pass
    