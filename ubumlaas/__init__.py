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

    v.app.logger.info("Creating and setting up application")
    v.app.logger.debug("basedir - %s", v.basedir)
    v.app.logger.debug("appdir - %s", v.appdir)

    ###########################################
    ############ CONFIGURATIONS ###############
    ###########################################

    ######################
    ### DATABASE SETUP ###
    ######################

    v.db = SQLAlchemy(app)
    Migrate(app, v.db)

    v.app.logger.info("Setting up DDBB")

    ######################
    #### EMAIL SETUP #####
    ######################

    mail = Mail(app)
    v.mail = mail
    if config_name == "main_app":
        ######################
        ##### BASE SETUP #####
        ######################

        v.app.logger.debug("Setting up Redis Workers")

        # Redis
        v.r = redis.Redis()
        #v.qm = Queue("medium-ubumlaas", connection=v.r, default_timeout=-1)
        v.qh = Queue("high-ubumlaas", connection=v.r, default_timeout=-1)
        BASE_WORKERS = 2
        HIGH_PRIORITIES_WORKERS = 5
        v.workers = 0
        #for _ in range(BASE_WORKERS):
        #    WorkerBuilder().set_queue(v.qm).create().start()
        for _ in range(HIGH_PRIORITIES_WORKERS):
            WorkerBuilder().set_queue(v.qh).create().start()

        #  Startup weka unofficial packages
        v.qh.enqueue(weka_packages.start_up_weka,
                    "ubumlaas/weka/weka_packages.json")

    ######################
    ###  LOGIN CONFIG  ###
    ######################

    v.app.logger.debug("Setting up Login Config")

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

    v.app.logger.debug("Registering BluePrints")

    def split_dict_key(cad):
        return cad.split(".")[-1]

    def hash_(cad):
        from flask_login import current_user
        if current_user.is_anonymous:
            v.app.logger.info("-1 - Getting anonymous user hash (0)")
            return 0
        else:
            v.app.logger.info("%d - Getting user hash", current_user.id)
            return hash(current_user.id)


    app.jinja_env.filters["split"] = split_dict_key
    app.jinja_env.filters["user"] = hash_

    return app
