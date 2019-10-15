"""Module with functions to execute training algorithms ready to enqueue.
"""
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

from ubumlaas import create_app
import pandas as pd
import variables as v
import traceback
import pickle

from ubumlaas.util import send_email
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
from ubumlaas.experiments.execute_algortihm import Execute_sklearn, Execute_weka

import tempfile
import shutil


def task_skeleton(experiment, current_user):
    """Base skeleton to execute an experiment.

    Arguments:
        experiment {dict} -- experiment information
                             (see model.Experiment.to_dict)
        current_user {dict} -- user information (see model.User.to_dict)
    """
    # Task need app environment
    create_app('subprocess')  # No generate new workers
    # Diference sklearn executor and weka executor
    apps_functions = {"sklearn": Execute_sklearn, "weka": Execute_weka}
    # Get algorithm type
    type_app = experiment["alg"]["alg_name"].split(".", 1)[0]
    try:
        execution_lib = apps_functions[type_app](experiment)
        
        X, y = execution_lib.open_dataset("ubumlaas/datasets/"+current_user["username"] +"/"
                           ,experiment['data'])

        #Find uniques values in weka and is classification
        execution_lib.find_y_uniques(y)

        #Training with and serialize all dataset
        models_dir = "ubumlaas/models/{}/".format(current_user["username"])
        if not os.path.exists(models_dir):
            os.makedirs(models_dir)
        model = execution_lib.create_model()
        execution_lib.train(model, X, y)
        execution_lib.serialize(model, "{}{}.model".format(models_dir, experiment['id']))

        #TODO find variable mode
        exp_config = execution_lib.experiment_configuration
        y_pred = None
        y_score = None
        if exp_config["mode"] == "split" and exp_config["train_partition"] < 100:
            X_train, X_test, y_train, y_test = execution_lib.generate_train_test_split(X, y, exp_config["train_partition"])
            model = execution_lib.create_model()
            execution_lib.train(model, X_train, y_train)
            y_pred, y_score = execution_lib.predict(model, X_test, y_test)
            y_pred = [y_pred]
            y_score = [y_score]
            y_test = [y_test]

        elif exp_config["mode"] == "cross":
            y_pred = []
            y_score = []
            y_test = []
            kfolds = execution_lib.generate_KFolds(X, y, exp_config["k_folds"])
            for X_train, X_test, y_train, y_test_kfold in kfolds:
                model = execution_lib.create_model()
                execution_lib.train(model, X_train, y_train)
                y_predk, y_scorek = execution_lib.predict(model, X_test, y_test_kfold)
                y_pred.append(y_predk)
                y_score.append(y_scorek)
                y_test.append(y_test_kfold)

        score = {}
        if exp_config["mode"] == "cross" or exp_config["train_partition"] < 100:
            
            typ = execution_lib.algorithm_type
            if typ == "Regression":
                score = regression_metrics(y_test, y_pred)
            elif typ == "Classification":
                score = classification_metrics(y_test, y_pred, y_score)
        result = json.dumps(score)
        state = 1
    except Exception as ex:
        # If algoritm failed it save traceback as result
        result = str(ex)
        print(traceback.format_exc())
        state = 2
    finally:
        execution_lib.close()
    
    from ubumlaas.models import Experiment
    print(result)
    exp = Experiment.query.filter_by(id=experiment['id']).first()
    exp.result = result
    exp.state = state
    exp.endtime = time()
    v.db.session.commit()

    send_email(current_user["username"], current_user["email"],
               experiment["id"], str(exp.result))
               
      
def classification_metrics(y_test_param, y_pred_param, y_score_param):
    """Compute classification metrics

    Arguments:
        y_test {1d array} -- test output
        y_pred {1d array} -- model output
        y_score {1d array} -- model score output

    Returns:
        dict -- metrics with computed value
    """
    score = {}

    for y_test, y_pred, y_score in zip(y_test_param,y_pred_param, y_score_param):

        # First confuse matrix
        conf_matrix = sklearn.metrics.confusion_matrix(y_test, y_pred)
        score.setdefault("confussion_matrix", []).append(conf_matrix.tolist())
        y_b_score = y_score.max(axis=1)
        if conf_matrix.shape[0] == 2:
            # Boolean metrics
            
            if y_test.dtype != np.bool:
                y_b_test, y_b_pred = value_to_bool(y_test.copy(), y_pred.copy())
            else:
                y_b_test = y_test
                y_b_pred = y_pred
            fpr, tpr, _ = sklearn.metrics.roc_curve(y_b_test, y_b_score)
            score.setdefault("ROC", []).append([fpr.tolist(), tpr.tolist()])
            score.setdefault("AUC", []).append(sklearn.metrics.auc(fpr, tpr))
            score.setdefault("kappa", []).append(sklearn.metrics.cohen_kappa_score(y_test, y_pred))
            score.setdefault("accuracy", []).append(sklearn.metrics.accuracy_score(y_test, y_pred))
            score.setdefault("f1_score", []).append(sklearn.metrics.f1_score(y_test, y_pred))

    return score


def value_to_bool(y_test, y_pred):
    """Transform a pandas non boolean column in boolean column

    Arguments:
        y_test {pandas} -- test output
        y_pred {pandas} -- model output

    Returns:
        [pandas,pandas] -- test output boolean, model output boolean
    """
    un = y_test.unique()
    d = {un[0]: True, un[1]: False}
    return y_test.map(d), pd.Series(y_pred).map(d)


def regression_metrics(y_test_param, y_pred_param):
    """Compute Regression metrics

    Arguments:
        y_test {pandas} -- test output
        y_pred {pandas} -- model output

    Returns:
        dict -- metrics with computed value
    """
    score = {}
    for y_test, y_pred in zip(y_test_param, y_pred_param):
        score.setdefault("max_error",[]).append(sklearn.metrics.max_error(y_test, y_pred))
        score.setdefault("mean_score_error", []).append(sklearn.metrics.mean_squared_error(y_test,
                                                                    y_pred))
        score.setdefault("mean_absolute_error", []).append(sklearn.metrics.mean_absolute_error(y_test,
                                                                        y_pred))

    return score

def execute_weka_predict(username,exp_id, tmp_filename, model_path,fil_name):


    
    try:
        create_app('subprocess') #No generate new workers
        upload_folder = "/tmp/"+username+"/"

    
        predict_df = get_dataframe_from_file(upload_folder, tmp_filename)
        

        from ubumlaas.models import Experiment, load_experiment
        experiment = load_experiment(exp_id)
        executor = Execute_weka(experiment.to_dict())
        class_attribute_name = executor.experiment_configuration["target"]

    

        # Open experiment configuration
        model_df = get_dataframe_from_file("ubumlaas/datasets/"+username +
                            "/", experiment.data)
        executor.find_y_uniques(model_df[class_attribute_name])
        
        predict_columns = predict_df.columns
        print(predict_columns)
        X = predict_df[executor.experiment_configuration["columns"]]
        if class_attribute_name in predict_columns:
            y = predict_df[class_attribute_name]
            predict_has_target = True
        else:
            y = ["?"]*len(predict_df.index)
            predict_has_target = False
        jvm.start(packages=True)


        model = executor.deserialize(model_path)
        
        y_pred, y_score = executor.predict(model, X, y)
    
        
        dataframes_final = [X]
        #remove "?" column if not exist original target
        if predict_has_target:
            dataframes_final.append(y)
            
        y_pred_df = pd.DataFrame(y_pred, columns=["prediction_"+class_attribute_name])
        dataframes_final.append(y_pred_df)
        dataframes = pd.concat(dataframes_final, axis=1)
        shutil.rmtree(upload_folder)
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)

        dataframes.to_csv(upload_folder + fil_name, index=None)
    except Exception:
        print(traceback.format_exc())
        return False
    finally:
        jvm.stop()
    return True

