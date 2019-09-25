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
            train_test_split(X, y,test_size=1-exp_config["split"]/100)
        models_dir ="ubumlaas/models/{}/".format(current_user["username"])
        if not os.path.exists(models_dir):
            os.makedirs(models_dir)
        y_pred = apps_functions[type_app](experiment,"{}{}.model".format(models_dir,experiment['id']), X_train, X_test, y_train, y_test)
     

       
        score_text = ""
        score = 0
        if experiment["alg"]["alg_typ"] == "Regression":
            score_text = "Mean squared error"
            score = sklearn.metrics.mean_squared_error(y_test, y_pred)
        elif experiment["alg"]["alg_typ"] == "Classification":
            score_text = "Confussion Matrix"
            score = sklearn.metrics.confusion_matrix(y_test, y_pred)
        state = 1
        result = score_text+": "+str(score)
    except Exception:
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
    model = eval(experiment["alg"]["alg_name"]+"()")
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    pickle.dump(model, open(path, 'wb'))

    return y_pred


def execute_weka(experiment, path, X_train, X_test, y_train, y_test):
    jvm.start(packages=True)
    
    data = create_weka_dataset(X_train , y_train)
    

    classifier = Classifier(classname=experiment["alg"]["alg_name"])
    
    classifier.build_classifier(data)
    data_test= create_weka_dataset(X_test,y_test)
    function = None
    if experiment["alg"]["alg_typ"] == "Classification":
        function = lambda p:data_test.class_attribute.value(int(p))
    elif experiment["alg"]["alg_typ"] == "Regression":
        function = lambda p: p
    y_pred=[]
    for instance in data_test:
        pred = classifier.classify_instance(instance)
        y_pred.append(function(pred))
      

    serialization.write(path, classifier)
    jvm.stop()

    return y_pred

def create_weka_dataset(X, y):
    try:
        temp = tempfile.NamedTemporaryFile()
        X_df =pd.DataFrame(X)
        y_df = pd.DataFrame(y)
        dataframe = pd.concat([X_df,y_df], axis=1)
        dataframe.to_csv(temp.name, index=None)
        y_uniques=y_df[y_df.columns[0]].unique()
        y_uniques.sort()
        loader = Loader(classname="weka.core.converters.CSVLoader",options=["-L","{}:{}".format(dataframe.shape[1],",".join(y_uniques))])
        data = loader.load_file(temp.name)
        #Last column of data is target
        data.class_is_last()
    finally:
        temp.close()
    return data