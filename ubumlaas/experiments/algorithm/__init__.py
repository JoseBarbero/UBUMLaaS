"""Module with functions to execute training algorithms ready to enqueue.
"""
import sklearn
import sklearn.base
import sklearn.cluster
import sklearn.linear_model
import sklearn.ensemble
import sklearn.neighbors
import sklearn.model_selection
import sklearn.preprocessing
import sklearn.multiclass
from ubumlaas.experiments.algorithm.metrics import calculate_metrics

from ubumlaas import create_app
import pandas as pd
import variables as v
import traceback

from ubumlaas.util import send_email
from time import time
import json
import os

import weka.core.jvm as jvm
from ubumlaas.util import get_dataframe_from_file
from ubumlaas.experiments.execute_algorithm._weka import Execute_weka

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
    # Get algorithm type
    type_app = experiment["alg"]["lib"]
    try:
        execution_lib = v.apps_functions[type_app](experiment)

        X, y = execution_lib.open_dataset("ubumlaas/datasets/"+current_user["username"] +"/",
                                          experiment['data'])

        #Find uniques values in weka and is classification
        execution_lib.find_y_uniques(y)

        #Training and serialize with all dataset
        models_dir = "ubumlaas/models/{}/".format(current_user["username"])
        if not os.path.exists(models_dir):
            os.makedirs(models_dir)
        model = execution_lib.create_model()
        execution_lib.train(model, X, y)
        execution_lib.serialize(model, "{}{}.model"
                                       .format(models_dir, experiment['id']))

        exp_config = execution_lib.experiment_configuration
        y_test = None
        y_pred = None
        y_score = None
        if execution_lib.algorithm_type == "Clustering":
            y_pred, y_score = execution_lib.predict(model, X)
        elif exp_config.get("mode") == "split" and exp_config["train_partition"] < 100:
            X_train, X_test, y_train, y_test = execution_lib.generate_train_test_split(X, y, exp_config["train_partition"])
            model = execution_lib.create_model()
            execution_lib.train(model, X_train, y_train)
            y_pred, y_score = execution_lib.predict(model, X_test)

        elif exp_config.get("mode") == "cross":
            y_pred = []
            y_score = []
            y_test = []
            kfolds = execution_lib.generate_KFolds(X, y, exp_config["k_folds"])
            for X_train, X_test, y_train, y_test_kfold in kfolds:
                model = execution_lib.create_model()
                execution_lib.train(model, X_train, y_train)
                y_predk, y_scorek = execution_lib.predict(model, X_test)
                y_pred.append(y_predk)
                y_score.append(y_scorek)
                y_test.append(y_test_kfold)

        score = {}
        if exp_config["mode"] == "cross" or exp_config["train_partition"] < 100 or execution_lib.algorithm_type == "Clustering":

            typ = execution_lib.algorithm_type
            score = calculate_metrics(typ, X, y_test, y_pred, y_score)
        result = json.dumps(score)
        state = 1
        print(result)
    except Exception as ex:
        # If algoritm failed it save traceback as result
        result = str(ex)
        print(traceback.format_exc())
        state = 2
    finally:
        execution_lib.close()

    from ubumlaas.models import Experiment
    exp = Experiment.query.filter_by(id=experiment['id']).first()
    exp.result = result
    exp.state = state
    exp.endtime = time()
    v.db.session.commit()

    send_email(current_user["username"], current_user["email"],
               experiment["id"], str(exp.result))


def execute_weka_predict(username, experiment, tmp_filename, model_path, fil_name):

    try:
        create_app('subprocess')  # No generate new workers
        upload_folder = "/tmp/"+username+"/"

        predict_df = get_dataframe_from_file(upload_folder, tmp_filename)

        executor = Execute_weka(experiment)
        class_attribute_name = executor.experiment_configuration["target"]

        # Open experiment configuration
        model_df = get_dataframe_from_file("ubumlaas/datasets/"+username +
                                           "/", experiment["data"])
        executor.find_y_uniques(model_df[class_attribute_name])

        predict_columns = predict_df.columns
        X = predict_df[executor.experiment_configuration["columns"]]
        if set(class_attribute_name) <= set(predict_columns):
            y = predict_df[class_attribute_name]
            predict_has_target = True
        else:
            y = ["?"]*len(predict_df.index)
            predict_has_target = False

        model = executor.deserialize(model_path)

        y_pred, y_score = executor.predict(model, X)

        dataframes_final = [X]
        #  remove "?" column if not exist original target
        if predict_has_target:
            dataframes_final.append(y)

        y_pred_df = pd.DataFrame(y_pred,
                                 columns=["prediction_" + name for name in class_attribute_name])
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
        executor.close()
    return True
