from ubumlaas.experiments.execute_algorithm import\
    (_meka, _weka, _sklearn, _is_ssl)
import os


def start():
    global login_manager, db, basedir, v, q, workers, app, apps_functions, mail, appdir

    login_manager = None
    db = None
    basedir = None
    appdir = None
    v = None
    q = None
    workers = None
    apps_functions = {"sklearn": _sklearn.Execute_sklearn,
                      "weka": _weka.Execute_weka,
                      "meka": _meka.Execute_meka,
                      "is_ssl": _is_ssl.Execute_ssl}
    app = None
    mail = None