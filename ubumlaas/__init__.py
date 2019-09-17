import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import variables as v
import redis
from rq import Queue
from ubumlaas.jobs import WorkerBuilder

import time
 
def create_app(config_name):
    v.start()
    app = Flask(__name__)

    ###########################################
    ############ CONFIGURATIONS ###############
    ###########################################

    # Remember you need to set your environment variables at the command line
    # when you deploy this to a real website.
    # export SECRET_KEY=mysecret
    # set SECRET_KEY=mysecret
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

    ######################
    ### DATABASE SETUP ###
    ######################
    v.basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///"+os.path.join(v.basedir, "data.sqlite")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    v.db = SQLAlchemy(app)
    Migrate(app, v.db)

    if config_name == "main_app":
        # Redis
        v.r = redis.Redis()
        v.q = Queue(connection=v.r)

        BASE_WORKERS = 3
        v.workers = 0
        for w in range(BASE_WORKERS):
            WorkerBuilder().set_queue(v.q).create().start()

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

    return app
