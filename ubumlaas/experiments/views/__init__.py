from flask import Blueprint

experiments = Blueprint("experiments", __name__)

import ubumlaas.experiments.views.experiment
import ubumlaas.experiments.views.dataset
import ubumlaas.experiments.views.predict
import ubumlaas.experiments.views.utils
