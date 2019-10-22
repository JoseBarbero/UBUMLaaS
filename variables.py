from ubumlaas.experiments.execute_algorithm import \
    (Execute_sklearn, Execute_weka, Execute_meka)


def start():
    global login_manager, db, basedir, v, q, workers, app, apps_functions

    login_manager = None
    db = None
    basedir = None
    v = None
    q = None
    workers = None
    apps_functions = {"sklearn": Execute_sklearn,
                      "weka": Execute_weka,
                      "meka": Execute_meka}
    app = None
