from abc import ABC, abstractmethod
from ubumlaas.util import get_dataframe_from_file
import json

from sklearn.model_selection import StratifiedKFold, KFold
import sklearn.model_selection
import variables as v

class Abstract_execute(ABC):

    def __init__(self, experiment):
        """Initizialice attributes from experiment dict

        Arguments:
            experiment {dict} -- experiment dictionary
        """
        self.id = experiment["id"]
        self.algorithm_name = experiment["alg"]["alg_name"]  # for example: weka.classification.trees.J48
        self.algorithm_configuration = Abstract_execute.__convert_to_dict(experiment["alg_config"])  # configuration algorithm
        self.configuration = Abstract_execute.__convert_to_dict(experiment["alg"]["config"])
        self.experiment_configuration = Abstract_execute.__convert_to_dict(experiment["exp_config"])
        self.algorithm_type = self.experiment_configuration["alg_type"]  # classification, reggression...

        v.app.logger.info("New execution - %d - %s - %s", self.id, self.algorithm_name, self.algorithm_type)

        if experiment.get("filter") is not None:            
            self.filter_name = experiment["filter"]["filter_name"]
            self.filter_config = Abstract_execute.__convert_to_dict(experiment["filter_config"])
            v.app.logger.info("Filtered - %d - %s - %s", self.id, self.algorithm_name, self.filter_name)
        else:
            self.filter_name = None
            v.app.logger.info("Not Filtered - %d - %s", self.id, self.algorithm_name)
        
        

    @staticmethod
    def __convert_to_dict(possible_json_str):
        """Convert to dictionary
        """
        if type(possible_json_str) != dict:
            possible_json_str = json.loads(possible_json_str)
        return possible_json_str

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
            y {DataFrame} -- targets columns
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
        #check if targets is not empty and some column from targets are in data column
        if len(self.experiment_configuration["target"]) !=0 and set(self.experiment_configuration["target"]) <= set(data.columns):
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

    def generate_train_test_split(self, X, y, train_size, random_state=None):
        """Generate train test split

        Arguments:
            X {DataFrame} -- attributes columns
            y {DataFrame} -- targets columns
            train_size {int} -- train size between 1 and 100

        Returns:
            [DataFrames] -- X_train, X_test, y_train, y_test
        """

        if y is None:
            X_train, X_test = sklearn.model_selection. \
            train_test_split(X, train_size=train_size/100,
                             random_state=self.experiment_configuration.get("random_seed", random_state))
            return X_train, X_test, None, None

        return sklearn.model_selection. \
            train_test_split(X, y, train_size=train_size/100,
                             random_state=self.experiment_configuration.get("random_seed", random_state))

    def generate_KFolds(self, X, y, n_splits=3, shuffle=True, random_state=None):
        """Generate KFolds

        Arguments:
            X {DataFrame} -- Attribute columns
            y {DataFrame} -- Target columns

        Keyword Arguments:
            n_splits {int} -- Number of folds. Must be at least 2. (default: {3})
            shuffle {bool} -- Whether to shuffle the data before splitting into batches. (default: {False})

        Returns:
            [list] -- list of tuples with X_train, X_test, y_train, y_test in each tuple
        """
        folds = []

        kf = self.kfold_algorithm()(n_splits=n_splits, shuffle=shuffle,
                                    random_state=self.experiment_configuration.get("random_seed", random_state))

        if y is None:
            for train_index, test_index in kf.split(X):

                X_train, X_test = X.iloc[train_index, :], \
                                X.iloc[test_index, :]

                folds.append((X_train, X_test, None, None))
            return folds
        
        for train_index, test_index in kf.split(X, y):

            X_train, X_test = X.iloc[train_index, :], \
                              X.iloc[test_index, :]

            y_train, y_test = y.iloc[train_index, :], y.iloc[test_index, :]
            folds.append((X_train, X_test, y_train, y_test))
        return folds

    def is_classification(self):
        """Check if the algorithm type is Classification

        Returns:
            [bool] -- True if algorithm is Classfication
        """
        return self.algorithm_type == "Classification"

    def has_filter(self):
        return self.filter_name is not None
