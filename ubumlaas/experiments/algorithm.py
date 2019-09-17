import sklearn
import sklearn.base
import sklearn.cluster
import sklearn.linear_model
import sklearn.metrics
import sklearn.model_selection
from ubumlaas import create_app
import pandas as pd
import variables as v

from ubumlaas.utils import send_email
from time import time

def task_skeleton(experiment, current_user):
    # Task need app environment
    model = eval(experiment["alg_name"]+"()")
    data = pd.read_csv("ubumlaas/datasets/"+current_user["username"]
        +"/"+experiment['data'])
    X = data.iloc[:, 0:-1]
    y = data.iloc[:, -1]
    X_train, X_test, y_train, y_test = \
        sklearn.model_selection.train_test_split(X, y, train_size=0.7, test_size=0.3)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    score = sklearn.metrics.explained_variance_score(y_test, y_pred)

    create_app('subprocess')
    from ubumlaas.models import Experiment

    exp = Experiment.query.filter_by(id=experiment['id']).first()

    exp.result = str(score)
    exp.endtime = time()
    v.db.session.commit()

    send_email(current_user["username"], current_user["email"], experiment["id"], str(exp.result))

    