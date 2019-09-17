from flask import render_template, url_for, flash, redirect, request, Blueprint
import variables as v
from ubumlaas.models import User, Experiment
from ubumlaas.experiments.forms import ExperimentForm
from flask_login import current_user, login_required
from flask_mail import Message
from time import time

experiments = Blueprint("experiments", __name__)

@login_required
@experiments.route("/new_experiment", methods=["GET", "POST"])
def new_experiment():

    form = ExperimentForm()

    if form.validate_on_submit():
        user = current_user
        exp = Experiment(user.id,form.alg_name.data,"DEFAULT", "sklearn.datasets.load_boston", None, time(), None)
        v.db.session.add(exp)
        v.db.session.commit()
       
    return render_template("experiment_form.html", form=form, title="Config experiment")