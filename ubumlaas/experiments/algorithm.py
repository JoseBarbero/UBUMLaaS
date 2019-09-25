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

from ubumlaas.utils import send_email
from time import time
import json

from weka.core import converters
import weka.core.jvm as jvm
from weka.classifiers import Classifier
from weka.core.classes import Random
from weka.classifiers import Evaluation


def task_skeleton(experiment, current_user):
    # Task need app environment
    create_app('subprocess')
    apps_functions = {"sklearn": execute_sklearn, "weka": execute_weka}
    type_app = experiment["alg"]["alg_name"].split(".", 1)[0]
    try:
        exp_config = json.loads(experiment["exp_config"])
        data = pd.read_csv("ubumlaas/datasets/"+current_user["username"] +
                           "/"+experiment['data'])
        X = data.loc[:, data.columns != exp_config["target"]]
        y = data[exp_config["target"]]
        X_train, X_test, y_train, y_test = \
            sklearn.model_selection. \
            train_test_split(X, y,
                             test_size=1-exp_config["split"]/100)

        model = apps_functions[type_app](experiment, X_train, y_train)

        y_pred = model.predict(X_test)
        score_text = ""
        score = 0
        if experiment["alg"]["alg_typ"] == "Regression":
            score_text = "Mean squared error"
            score = sklearn.metrics.mean_squared_error(y_test, y_pred)
        elif experiment["alg"]["alg_typ"] == "Classification":
            score_text = "Confussion Matrix"
            score = sklearn.metrics.confusion_matrix(y_test, y_pred)

    except Exception as ex:
        result = str(ex)
        raise
        state = 2

    from ubumlaas.models import Experiment

    exp = Experiment.query.filter_by(id=experiment['id']).first()
    exp.result = result
    exp.state = state
    exp.endtime = time()
    v.db.session.commit()

    send_email(current_user["username"], current_user["email"], experiment["id"], str(exp.result))


def execute_sklearn(experiment, X_train, y_train):
    alg_config = json.loads(experiment["alg_config"])
    print(alg_config)
    model = eval(experiment["alg"]["alg_name"]+"(**alg_config)")
    model.fit(X_train, y_train)

    return model

def execute_weka(experiment, X_train, y_train):
    jvm.start()
    data_dir = "ubumlaas/datasets/"+current_user["username"]+"/"+experiment["data"]
    data = converters.load_any_file(data_dir)
    #Last column of data is target
    data.class_is_last()

    classifier = Classifier(classname=experiment["alg"]["alg_name"])

    evaluation = Evaluation(data)
    evaluation.evaluate_train_test_split(classifier, data, 70.0, Random(time()))
    result = evaluation.summary()
    state = 1        

    jvm.stop()

    return result, state
