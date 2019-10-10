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

from ubumlaas.utils import send_email
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

import tempfile


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
    apps_functions = {"sklearn": execute_sklearn, "weka": execute_weka}
    # Get algorithm type
    type_app = experiment["alg"]["alg_name"].split(".", 1)[0]
    try:
        exp_config = json.loads(experiment["exp_config"])
        # Open experiment configuration
        data = pd.read_csv("ubumlaas/datasets/"+current_user["username"] +
                           "/"+experiment['data'])
        X = data.loc[:, exp_config["columns"]]
        y = data[exp_config["target"]]
        # Split dataset (if unsupervised it will be modified)
        X_train, X_test, y_train, y_test = \
            sklearn.model_selection. \
            train_test_split(X, y, test_size=1-exp_config["split"]/100)

        models_dir = "ubumlaas/models/{}/".format(current_user["username"])
        if not os.path.exists(models_dir):
            os.makedirs(models_dir)
        y_pred, y_score = apps_functions[type_app](experiment,
                                          "{}{}.model".
                                          format(models_dir, experiment['id']),
                                          X_train, X_test, y_train, y_test)

        score_text = ""
        score = 0
        if experiment["alg"]["alg_typ"] == "Regression":
            score = regression_metrics(y_test, y_pred)
        elif experiment["alg"]["alg_typ"] == "Classification":
            score = classification_metrics(y_test, y_pred, y_score)
        state = 1
        result = json.dumps(score)
    except Exception as ex:
        # If algoritm failed it save traceback as result
        result = str(ex)
        print(traceback.format_exc())
        state = 2

    from ubumlaas.models import Experiment

    exp = Experiment.query.filter_by(id=experiment['id']).first()
    exp.result = result
    exp.state = state
    exp.endtime = time()
    v.db.session.commit()

    send_email(current_user["username"], current_user["email"],
               experiment["id"], str(exp.result))


def __create_sklearn_model(alg_name, alg_config):
    """Create a sklearn model recursive

    Arguments:
        alg_name {string} -- sklearn model name
        alg_config {dict} -- parameters
    """
    for ac in alg_config:
        if type(alg_config[ac]) == dict:
            alg_config[ac] = __create_sklearn_model(
                                    alg_config[ac]["alg_name"],
                                    alg_config[ac]["parameters"])

    model = eval(alg_name+"(**alg_config)")
    return model


def execute_sklearn(experiment, path, X_train, X_test, y_train, y_test):
    """It trains a sklearn model

    Arguments:
        experiment {dict} -- experiment information (see model.Experiment.to_dict)
        path {str} -- directory to save model
        X_train {dataframe} -- training input
        X_test {dataframe} -- test input
        y_train {dataframe} -- training output
        y_test {dataframe} -- test output

    Returns:
        dataframe -- output of X_test in trained model.
    """
    alg_config = json.loads(experiment["alg_config"])
    model = __create_sklearn_model(experiment["alg"]["alg_name"], alg_config)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    y_score = None
    if (experiment["alg"]["alg_typ"] == "Classification"):
        y_score = model.predict_proba(X_test)

    pickle.dump(model, open(path, 'wb'))

    return y_pred, y_score


def execute_weka(experiment, path, X_train, X_test, y_train, y_test):
    """It trains a weka model

    Arguments:
        experiment {dict} -- experiment information (see model.Experiment.to_dict)
        path {str} -- directory to save model
        X_train {dataframe} -- training input
        X_test {dataframe} -- test input
        y_train {dataframe} -- training output
        y_test {dataframe} -- test output

    Returns:
        y_pred {array of predictions} 
        y_score {2d array of class distribution of every instance}
    """
    jvm.start(packages=True)

    alg_config = json.loads(experiment["alg_config"])

    conf = json.loads(experiment["alg"]["config"])

    lincom = []

    for i in alg_config.keys():
        v = alg_config[i]
        if v is not False:
            lincom.append(conf[i]["command"])
        if not isinstance(v, bool):
            lincom.append(str(v))

    data = create_weka_dataset(X_train, y_train)

    classifier = Classifier(classname=experiment["alg"]["alg_name"], options=lincom)

    classifier.build_classifier(data)
    data_test = create_weka_dataset(X_test, y_test)
    function = None
    y_score = None
    if experiment["alg"]["alg_typ"] == "Classification":
        function = lambda p: data_test.class_attribute.value(int(p))
        y_score = classifier.distributions_for_instances(data_test)
    elif experiment["alg"]["alg_typ"] == "Regression":
        function = lambda p: p
    y_pred = []
    for instance in data_test:
        pred = classifier.classify_instance(instance)
        y_pred.append(function(pred))

    serialization.write(path, classifier)
    jvm.stop()

    try: #Trying to convert to int
        y_pred = [int(pred) for pred in y_pred]
    except ValueError:
        pass

    return y_pred, y_score


def create_weka_dataset(X, y):
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
        X_df = pd.DataFrame(X)
        y_df = pd.DataFrame(y)
        dataframe = pd.concat([X_df, y_df], axis=1)
        dataframe.to_csv(temp.name, index=None)

        # Find uniques values from target
        y_uniques = y_df[y_df.columns[0]].unique()
        y_uniques.sort()
        loader = Loader(classname="weka.core.converters.CSVLoader",
                        options=["-L", "{}:{}".format(dataframe.shape[1],
                                 ",".join(map(str, y_uniques)))])
        data = loader.load_file(temp.name)
        # Last column of data is target
        data.class_is_last()
    finally:
        temp.close()
    return data


def classification_metrics(y_test, y_pred, y_score):
    """Compute classification metrics

    Arguments:
        y_test {1d array} -- test output
        y_pred {1d array} -- model output
        y_score {1d array} -- model score output

    Returns:
        dict -- metrics with computed value
    """
    score = {}



    # First confuse matrix
    conf_matrix = sklearn.metrics.confusion_matrix(y_test, y_pred)
    score["confussion_matrix"] = conf_matrix.tolist()
    y_b_score = y_score.max(axis=1)
    if conf_matrix.shape[0] == 2:
        # Boolean metrics
        if y_test.dtype != np.bool:
            y_b_test, y_b_pred = value_to_bool(y_test.copy(), y_pred.copy())
        else:
            y_b_test = y_test
            y_b_pred = y_pred
        fpr, tpr, _ = sklearn.metrics.roc_curve(y_b_test, y_b_score)
        score["ROC"] = [fpr.tolist(), tpr.tolist()]
        score["AUC"] = sklearn.metrics.auc(fpr, tpr)
        score["kappa"] = sklearn.metrics.cohen_kappa_score(y_test, y_pred)
        score["accuracy"] = sklearn.metrics.accuracy_score(y_test, y_pred)
        score["f1_score"] = sklearn.metrics.f1_score(y_test, y_pred)

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


def regression_metrics(y_test, y_pred):
    """Compute Regression metrics

    Arguments:
        y_test {pandas} -- test output
        y_pred {pandas} -- model output

    Returns:
        dict -- metrics with computed value
    """
    score = {}

    score["max_error"] = sklearn.metrics.max_error(y_test, y_pred)
    score["mean_score_error"] = sklearn.metrics.mean_squared_error(y_test,
                                                                   y_pred)
    score["mean_absolute_error"] = sklearn.metrics.mean_absolute_error(y_test,
                                                                       y_pred)

    return score
