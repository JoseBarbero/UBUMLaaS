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


def task_skeleton(experiment, current_user):
    # Task need app environment
    create_app('subprocess')
    try:
        model = eval(experiment["alg"]["alg_name"]+"()")
        data = pd.read_csv("ubumlaas/datasets/"+current_user["username"]
        +"/"+experiment['data'])
        X = data.iloc[:, 0:-1]
        y = data.iloc[:, -1]
        X_train, X_test, y_train, y_test = \
            sklearn.model_selection.train_test_split(X, y, train_size=0.7, test_size=0.3)
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)
        score_text = ""
        score = 0
        if experiment["alg"]["alg_typ"] == "Regression":
            score_text = "Mean squared error"
            score = sklearn.metrics.mean_squared_error(y_test, y_pred)
        elif experiment["alg"]["alg_typ"] == "Classification":
            score_text = "Confussion Matrix"
            score = sklearn.metrics.confusion_matrix(y_test, y_pred)
        result = score_text+": "+str(score)
        state = 1
    except Exception as ex:
        result = str(ex)
        #raise
        state = 2

    from ubumlaas.models import Experiment

    exp = Experiment.query.filter_by(id=experiment['id']).first()

    exp.result = result
    exp.state = state
    exp.endtime = time()
    v.db.session.commit()

    send_email(current_user["username"], current_user["email"], experiment["id"], str(exp.result))

    