from os import environ
import variables as v
import json
import unittest
from ubumlaas.experiments.algorithm.metrics import calculate_metrics
from ubumlaas import create_app

class TestMeka(unittest.TestCase):
        execute = None
        experiment = json.load(open("test/json/music.json", "r"))
        @classmethod
        def setUpClass(cls):
                create_app('subprocess')  # No generate new workers
                TestMeka.execute = v.apps_functions[TestMeka.experiment["alg"]["lib"]](TestMeka.experiment)


        def test_enviroment_variable(self):
                self.assertTrue("MEKA_CLASSPATH" in environ, "MEKA_CLASSPATH enviroment variable not found")
                self.assertTrue("JAVA_HOME" in environ, "JAVA_HOME enviroment variable not found")

        def test_open_dataset(self):
                X, y = TestMeka.execute.open_dataset("test/datasets/",TestMeka.experiment["data"])
                self.assertEqual(X.shape, (592,71))
                self.assertEqual(y.shape, (592, 6))
                return X, y

        def test_create_model(self):
                model = TestMeka.execute.create_model()
                return model

        def test_train_test_split(self, X = None, y = None, train_size = 70):

                
                X, y = self.test_open_dataset()

                X_train, X_test, y_train, y_test = TestMeka.execute.generate_train_test_split(X, y, train_size)
                
                self.assertEqual(X_train.shape[0], y_train.shape[0]) #compare if has same row length between X_train and y_train
                self.assertEqual(X_test.shape[0], y_test.shape[0])

                return X_train, X_test, y_train, y_test

        def test_kfold(self, n_splits = 3):
                
                X, y = self.test_open_dataset()
                kfold = TestMeka.execute.generate_KFolds(X, y, n_splits=n_splits)
                self.assertEqual(len(kfold), n_splits)
                return kfold

        def test_fit_and_predict(self):
                model = self.test_create_model()
                X_train, X_test, y_train, y_test = self.test_train_test_split()
                TestMeka.execute.train(model, X_train, y_train)
                y_pred, y_score = TestMeka.execute.predict(model, X_test)
                list_y_pred = [y_pred]
                list_y_test = [y_test]
                list_y_score = [y_score]

                score = calculate_metrics(TestMeka.execute.algorithm_type, list_y_test,list_y_pred, list_y_score)

                self.assertEqual(len(y_pred), y_test.shape[0])
                self.assertIsNone(y_score)

                return y_pred, score

        def test_fit_and_predict_kfold(self):
                list_y_pred = []
                list_y_score = []
                list_y_test = []
                kfolds = self.test_kfold(5)
                for X_train, X_test, y_train, y_test in kfolds:
                        model = TestMeka.execute.create_model()
                        TestMeka.execute.train(model, X_train, y_train)
                        y_pred, y_score = TestMeka.execute.predict(model, X_test)
                        list_y_pred.append(y_pred)
                        list_y_score.append(y_score)
                        list_y_test.append(y_test)

                score = calculate_metrics(TestMeka.execute.algorithm_type, list_y_test,list_y_pred, list_y_score)
if __name__ == '__main__':
        unittest.main()