from os import environ
import variables as v
import json
import unittest
from ubumlaas.experiments.algorithm.metrics import calculate_metrics
import tempfile
import os
import weka.core.packages as packages

class ParametrizedTestCase(unittest.TestCase):
        """ TestCase classes that want to be parametrized should
                inherit from this class.
        """
        def __init__(self, methodName='runTest', path = None):
                super().__init__(methodName)
                self.experiment = json.load(open(path, "r"))
                self.execute = v.apps_functions[self.experiment["alg"]["lib"]](self.experiment)

        @staticmethod
        def parametrize(testcase_klass, param=None):
                """ Create a suite containing all tests taken from the given
                subclass, passing them the parameter 'param'.
                """
                testloader = unittest.TestLoader()
                testnames = testloader.getTestCaseNames(testcase_klass)
                suite = unittest.TestSuite()
                for name in testnames:
                        suite.addTest(testcase_klass(name, param))
                return suite

class ExecuteLibsTest(ParametrizedTestCase):

        def test_enviroment_variable(self):
                """Test if exists enviroment variables
                """
                self.assertTrue("MEKA_CLASSPATH" in environ, "MEKA_CLASSPATH enviroment variable not found")
                self.assertTrue("JAVA_HOME" in environ, "JAVA_HOME enviroment variable not found")
                self.assertTrue("WEKA_HOME" in environ, "WEKA_HOME enviroment variable not found")
                items = packages.installed_packages()
                for item in items:
                        self.assertTrue(item.name in environ["MEKA_CLASSPATH"], item.name +" not in MEKA_CLASSPATH")

        def test_open_dataset(self):
                """Test open dataset for columns and target 
                
                Returns:
                    dataframe, dataframe -- dataframes for columns and target(s)
                """
                X, y = self.execute.open_dataset("test/datasets/",self.experiment["data"])
                self.assertEqual(X.shape[1], len(self.execute.experiment_configuration["columns"]))
                self.assertEqual(y.shape[1], len(self.execute.experiment_configuration["target"]))
                self.execute.find_y_uniques(y)
                return X, y

        def test_create_model(self):
                """Test create model with the configuration paramaeter
                
                Returns:
                    [object] -- model
                """
                model = self.execute.create_model()
                
                return model

        def test_train_test_split(self, train_size = 70):
                """Create train test split with the dataset
                
                Keyword Arguments:
                    train_size {int} -- train size (default: {70})
                
                Returns:
                    [dataframe] -- X_train, X_test, y_train, y_test
                """
                
                X, y = self.test_open_dataset()

                X_train, X_test, y_train, y_test = self.execute.generate_train_test_split(X, y, train_size)
                
                self.assertEqual(X_train.shape[0], y_train.shape[0]) #compare if has same row length between X_train and y_train
                self.assertEqual(X_test.shape[0], y_test.shape[0])

                return X_train, X_test, y_train, y_test

        def test_kfold(self, n_splits = 3):
                """Create kfolds 
                
                Keyword Arguments:
                    n_splits {int} --number of splits (default: {3})
                
                Returns:
                    [list of tuples] -- list of tuples with X_train, X_test, y_train, y_test in every tuple
                """

                X, y = self.test_open_dataset()
                kfold = self.execute.generate_KFolds(X, y, n_splits=n_splits)
                self.assertEqual(len(kfold), n_splits)
                return kfold

        def test_fit_and_predict_split(self):
                """Train model and prediction with train_test_split
                """
                model = self.execute.create_model()
                if self.execute.experiment_configuration["mode"] == "split":
                        X_train, X_test, y_train, y_test = self.test_train_test_split(self.execute.experiment_configuration["train_partition"])
                else:
                        X_train, X_test, y_train, y_test = self.test_train_test_split()
                
                self.execute.train(model, X_train, y_train)
                y_pred, y_score = self.execute.predict(model, X_test)
                list_y_pred = [y_pred]
                list_y_test = [y_test]
                list_y_score = [y_score]

                calculate_metrics(self.execute.algorithm_type, list_y_test,list_y_pred, list_y_score)

                self.assertEqual(len(y_pred), y_test.shape[0])

        def test_fit_and_predict_kfold(self):
                """Train model and prediction with k_folds
                """
                list_y_pred = []
                list_y_score = []
                list_y_test = []
                if self.execute.experiment_configuration["mode"] == "cross":
                        kfolds = self.test_kfold(self.execute.experiment_configuration["k_folds"])
                else:
                        kfolds = self.test_kfold()

                for X_train, X_test, y_train, y_test in kfolds:
                        model = self.execute.create_model()
                        self.execute.train(model, X_train, y_train)
                        y_pred, y_score = self.execute.predict(model, X_test)
                        list_y_pred.append(y_pred)
                        list_y_score.append(y_score)
                        list_y_test.append(y_test)

                calculate_metrics(self.execute.algorithm_type, list_y_test,list_y_pred, list_y_score)

        def test_serialize_deserialize(self):
                """Test to serialize and deserialize the model with the same dataset in train and predict
                """

                X, y = self.test_open_dataset()
                model = self.test_create_model()
                with tempfile.NamedTemporaryFile(delete=False) as temp:
                        temp_name = temp.name
                        self.execute.train(model, X, y)
                        self.execute.serialize(model, temp_name)
                model = self.execute.deserialize(temp_name)
                y_pred, y_score = self.execute.predict(model, X)
                calculate_metrics(self.execute.algorithm_type, [y],[y_pred], [y_score])
                
                if os.path.exists(temp_name):
                        os.remove(temp_name)