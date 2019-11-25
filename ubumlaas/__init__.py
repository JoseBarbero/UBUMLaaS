import os
from flask import Flask, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import variables as v
import redis
from rq import Queue
from ubumlaas.jobs import WorkerBuilder
import ubumlaas.weka.weka_packages as weka_packages
from flask_mail import Mail
import time
import json
import logging.config


def create_app(config_name):
    """ Creata application.

    Arguments:
        config_name {string} -- configuration.

    Returns:
        Flask -- flask application.
    """
    v.start()
    v.basedir = os.path.abspath(os.path.dirname(__file__))
    v.appdir = os.path.join(v.basedir,"..")
    # loggin setup
    import ubumlaas.logger
    ubumlaas.logger.create_folders_if_needed()
    logging.config.dictConfig(json.load(open(os.getenv("LOGGING_CONFIG") or "logging_config.json")))
    app = Flask(__name__)
    v.app = app
    app.config.from_pyfile('../config.py') # from config.py
    ###########################################
    ############ CONFIGURATIONS ###############
    ###########################################

    ######################
    ### DATABASE SETUP ###
    ######################

    v.db = SQLAlchemy(app)
    Migrate(app, v.db)

    ######################
    #### EMAIL SETUP #####
    ######################

    mail = Mail(app)
    v.mail = mail
    if config_name == "main_app":
        ######################
        ##### BASE SETUP #####
        ######################
        # Redis
        v.r = redis.Redis()
        v.q = Queue("medium-ubumlaas", connection=v.r, default_timeout=-1)

        BASE_WORKERS = 3
        v.workers = 0
        for _ in range(BASE_WORKERS):
            WorkerBuilder().set_queue(v.q).create().start()

        #  Startup weka unofficial packages
        v.q.enqueue(weka_packages.start_up_weka,
                    "ubumlaas/weka/weka_packages.json")

    ######################
    ###  LOGIN CONFIG  ###
    ######################
    v.login_manager = LoginManager()

    v.login_manager.init_app(app)
    v.login_manager.login_view = "users.login"

    ###########################
    #### BLUEPRINT CONFIGS ####
    ###########################

    from ubumlaas.core.views import core
    from ubumlaas.users.views import users
    from ubumlaas.error_pages.handlers import error_pages
    from ubumlaas.experiments.views import experiments
    app.register_blueprint(core)
    app.register_blueprint(users)
    app.register_blueprint(error_pages)
    app.register_blueprint(experiments)

    def split_dict_key(cad):
        return cad.split(".")[-1]

    app.jinja_env.filters["split"] = split_dict_key

    return app
