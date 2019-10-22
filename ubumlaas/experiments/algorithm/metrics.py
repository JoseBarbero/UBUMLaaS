import sklearn.metrics as mtr
import numpy as np
from ubumlaas.util import value_to_bool


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
        if conf_matrix.shape[0] == 2:
            # Boolean metrics

            if y_test.values.dtype != np.bool:
                y_b_test, y_b_pred = \
                    value_to_bool(y_test.copy(), y_pred.copy())
            else:
                y_b_test = y_test
            fpr, tpr, _ = mtr.roc_curve(y_b_test, y_b_score)
            score.setdefault("ROC", []).append([fpr.tolist(), tpr.tolist()])
            score.setdefault("AUC", []).append(mtr.auc(fpr, tpr))
            score.setdefault("kappa", []).append(mtr.cohen_kappa_score(y_test,
                                                                       y_pred))
            score.setdefault("accuracy", []).append(mtr.accuracy_score(y_test,
                                                                       y_pred))
            score.setdefault("f1_score", []).append(mtr.f1_score(y_test,
                                                                 y_pred))

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
        score.setdefault("max_error", []).\
            append(mtr.max_error(y_test, y_pred))
        score.setdefault("mean_score_error", []).\
            append(mtr.mean_squared_error(y_test, y_pred))
        score.setdefault("mean_absolute_error", []).\
            append(mtr.mean_absolute_error(y_test, y_pred))

    return score
