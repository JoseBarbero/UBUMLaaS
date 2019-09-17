from flask import render_template, url_for, flash, redirect, request, Blueprint
import variables as v
from ubumlaas.models import User, Experiment, load_user
from ubumlaas.experiments.forms import ExperimentForm
from flask_login import current_user, login_required
from flask_mail import Message
from time import time

from ubumlaas.experiments.algorithm import task_skeleton

experiments = Blueprint("experiments", __name__)

@login_required
@experiments.route("/new_experiment", methods=["GET", "POST"])
def new_experiment():

    form = ExperimentForm()
    form.dataset_list()

    if form.validate_on_submit():
        user = current_user
        exp = Experiment(user.id, form.alg_name.data, "DEFAULT",
            form.data.data, None, time(), None)
        v.db.session.add(exp)
        v.db.session.commit()
        v.q.enqueue(task_skeleton, args=(exp.to_dict(), user.to_dict()))
       
    return render_template("experiment_form.html", form=form, title="Config experiment")