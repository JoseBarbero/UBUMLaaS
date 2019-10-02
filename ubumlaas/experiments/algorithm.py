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
from ubumlaas import create_app
import pandas as pd
import variables as v
import traceback
import pickle

from ubumlaas.utils import send_email
from time import time
import json
import os

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
        experiment {dict} -- experiment information (see model.Experiment.to_dict)
        current_user {dict} -- user information (see model.User.to_dict)
    """
    # Task need app environment
    create_app('subprocess') #No generate new workers
    #Diference sklearn executor and weka executor
    apps_functions = {"sklearn": execute_sklearn, "weka": execute_weka}
    #Get algorithm type
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
            score_text = "Mean squared error"
            score = sklearn.metrics.mean_squared_error(y_test, y_pred)
        elif experiment["alg"]["alg_typ"] == "Classification":
            score_text = "Confussion Matrix"
            score = sklearn.metrics.confusion_matrix(y_test, y_pred, y_score)
        state = 1
        result = score_text+": "+str(score)
    except Exception:
        # If algoritm failed it save traceback as result
        result = str(traceback.format_exc())
        state = 2

    from ubumlaas.models import Experiment

    exp = Experiment.query.filter_by(id=experiment['id']).first()
    exp.result = result
    exp.state = state
    exp.endtime = time()
    v.db.session.commit()

    send_email(current_user["username"], current_user["email"], experiment["id"], str(exp.result))


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
    model = eval(experiment["alg"]["alg_name"]+"(**alg_config)")
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
        dataframe -- output of X_test in trained model.
    """
    jvm.start(packages=True)

    alg_config = json.loads(experiment["alg_config"])

    conf = json.loads(experiment["alg"]["config"])

    lincom = []

    for i in alg_config.keys():
        v = alg_config[i]
        if v is not False:
            lincom.append(conf[i]["command"])
        if not isinstance(v,bool):
            lincom.append(str(v))

    print(lincom)


    data = create_weka_dataset(X_train, y_train)

    classifier = Classifier(classname=experiment["alg"]["alg_name"], options=lincom)

    classifier.build_classifier(data)
    data_test = create_weka_dataset(X_test, y_test)
    function = None
    if experiment["alg"]["alg_typ"] == "Classification":
        function = lambda p: data_test.class_attribute.value(int(p))
    elif experiment["alg"]["alg_typ"] == "Regression":
        function = lambda p: p
    y_pred = []
    for instance in data_test:
        pred = classifier.classify_instance(instance)
        y_pred.append(function(pred))

    serialization.write(path, classifier)
    jvm.stop()

    return y_pred


def create_weka_dataset(X, y):
    try:
        temp = tempfile.NamedTemporaryFile()
        X_df = pd.DataFrame(X)
        y_df = pd.DataFrame(y)
        dataframe = pd.concat([X_df, y_df], axis=1)
        dataframe.to_csv(temp.name, index=None)
        y_uniques = y_df[y_df.columns[0]].unique()
        y_uniques.sort()
        loader = Loader(classname="weka.core.converters.CSVLoader",
                        options=["-L", "{}:{}".format(dataframe.shape[1],
                                 ",".join(y_uniques))])
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
        y_pred {[type]} -- model output
    
    Returns:
        dict -- metrics with computed value
    """
    score = {}

    # First confuse matrix
    conf_matrix = sklearn.metrics.confusion_matrix(y_test, t_pred)
    score["conf_matrix"] = conf_matrix
    if conf_matrix.shape[0] == 2:
        # Boolean metrics
        if y_test.dtype == np.bool:
            fpr, tpr = sklearn.metrics.roc_curve(y_test, y_score)
            score["ROC"] = [fpr, tpr]
            score["AUC"] = sklearn.metrics.auc(fpr, tpr)

    return score