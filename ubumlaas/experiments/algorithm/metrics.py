import sklearn.metrics as mtr
import numpy as np
import pandas as pd
from ubumlaas.util import value_to_bool, find_y_uniques
from sklearn.preprocessing import LabelBinarizer
import variables as v
from flask_login import current_user

def calculate_metrics(typ, y_test, y_pred, y_score, X = None):
    score = {}

    if typ == "Regression" or typ == "MultiRegression":
        score = regression_metrics(y_test, y_pred)
    elif typ == "Classification":
        score = classification_metrics(y_test, y_pred, y_score)
    elif typ == "MultiClassification":
        score = multiclassication_metrics(y_test, y_pred)
    elif typ == "Clustering":
        score = clustering_metrics(X, y_pred)
    v.app.logger.info("Calculating %s metrics", typ)
    v.app.logger.debug("Score of %s metrics: %s",typ, score)
    return score


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

    for y_test, y_pred, y_score in \
            zip(y_test_param, y_pred_param, y_score_param):

        # First confuse matrix
        conf_matrix = mtr.confusion_matrix(y_test, y_pred)
        
        score.setdefault("confussion_matrix", []).append(conf_matrix.tolist())
        y_b_score = y_score.max(axis=1)
        if conf_matrix.shape[0] == 2 and y_test.iloc[:, 0].dtype != np.bool:
            y_b_test, _ = \
                value_to_bool(y_test.iloc[:, 0].copy(), y_pred.copy())
        else:
            y_b_test = y_test

        if conf_matrix.shape[0] == 2:
            fpr, tpr, _ = mtr.roc_curve(y_b_test, y_b_score)
            score.setdefault("ROC", []).append([fpr.tolist(), tpr.tolist()])
            score.setdefault("AUC", []).append(mtr.auc(fpr, tpr))
            print(y_test.values[0][0])
            score.setdefault("f1_score", []).append(mtr.f1_score(y_test,
                                                                 y_pred,
                                                                 pos_label=y_test.values[0][0]))
        else:
            score.setdefault("AUC", [])\
                .append(multiclass_roc_auc_score(y_test, y_pred))
            score.setdefault("f1_score", [])\
                .append(mtr.f1_score(y_test, y_pred, average="macro"))

        score.setdefault("kappa", []).append(mtr.cohen_kappa_score(y_test,
                                                                   y_pred))
        score.setdefault("accuracy", []).append(mtr.accuracy_score(y_test,
                                                                   y_pred))

    conf_matrix_final = np.array(score["confussion_matrix"])
    if len(conf_matrix_final) > 1:
            conf_mean = [conf_matrix_final.mean(0)]
            score["confussion_matrix"] = np.concatenate((conf_matrix_final,conf_mean),axis=0).tolist()

    return score


def multiclassication_metrics(y_test_param, y_pred_param):
    score = {}

    for y_test, y_pred in zip(y_test_param, y_pred_param):
        score.setdefault("accuracy", []).\
            append(mtr.accuracy_score(y_test, y_pred))
        score.setdefault("hamming_loss", []).\
            append(mtr.hamming_loss(y_test, y_pred))
        score.setdefault("f1_score_micro", []).\
            append(mtr.f1_score(y_test, y_pred, average="micro"))
        score.setdefault("f1_score_macro", []).\
            append(mtr.f1_score(y_test, y_pred, average="macro"))
        score.setdefault("zero_one_loss", []).\
            append(mtr.zero_one_loss(y_test, y_pred))
        score.setdefault("label_ranking_loss", []).\
            append(mtr.label_ranking_loss(y_test, y_pred))

    return score


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
        set_score(score, "max_error", mtr.max_error(y_test, y_pred))
        set_score(score, "mean_score_error", mtr.mean_squared_error(y_test, y_pred))
        set_score(score, "mean_absolute_error", mtr.mean_absolute_error(y_test, y_pred))


    return score


def multiclass_roc_auc_score(y_test, y_pred, average="macro"):
    lb = LabelBinarizer()
    lb.fit(y_test)
    y_test = lb.transform(y_test)
    y_pred = lb.transform(y_pred)

    return mtr.roc_auc_score(y_test, y_pred, average=average)


def clustering_metrics(list_X, list_y_pred):
    score = {}
    for X, y_pred in zip(list_X, list_y_pred):
        if len(find_y_uniques(pd.Series(y_pred)))>1:
            set_score(score, "calinski_harabasz_score", mtr.calinski_harabasz_score(X, y_pred))
            set_score(score, "davies_bouldin_score", mtr.davies_bouldin_score(X, y_pred))
            set_score(score, "silhouette_score", mtr.silhouette_score(X, y_pred))
    return score


def set_score(score, key, value):
    score.setdefault(key, []).append(value)

