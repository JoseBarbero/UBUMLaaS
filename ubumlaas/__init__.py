import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
<<<<<<< HEAD
from celery import Celery
from config import Config
import variables as v
 
celery = Celery(__name__, broker=Config.CELERY_BROKER_URL)

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

    ######################
    ###  LOGIN CONFIG  ###
    ######################
    v.login_manager = LoginManager()

    v.login_manager.init_app(app)
    v.login_manager.login_view = "users.login"

    ### Celery
    celery.conf.update(app.config)

    ###########################
    #### BLUEPRINT CONFIGS ####
    ###########################

    from ubumlaas.core.views import core
    from ubumlaas.users.views import users
    from ubumlaas.error_pages.handlers import error_pages
    app.register_blueprint(core)
    app.register_blueprint(users)
    app.register_blueprint(error_pages)

    return app
=======

app = Flask(__name__)

###########################################
############ CONFIGURATIONS ###############
###########################################

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

######################
### DATABASE SETUP ###
######################
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///"+os.path.join(basedir,"data.sqlite")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
Migrate(app, db)

######################
###  LOGIN CONFIG  ###
######################
login_manager = LoginManager()

login_manager.init_app(app)
login_manager.login_view = "users.login"

###########################
#### BLUEPRINT CONFIGS ####
###########################

from ubumlaas.core.views import core
from ubumlaas.users.views import users
from ubumlaas.error_pages.handlers import error_pages
app.register_blueprint(core)
app.register_blueprint(users)
app.register_blueprint(error_pages)
>>>>>>> e75262213bcf0786402b005504f5dc2f4ba9ae3b
