from flask import render_template, url_for, flash, redirect, request, Blueprint
import variables as v
from ubumlaas.models import User, Experiment, load_user
from ubumlaas.experiments.forms import ExperimentForm, DatasetForm
from flask_login import current_user, login_required
from flask_mail import Message
from time import time
from werkzeug.utils import secure_filename
import os
import pandas as pd

from ubumlaas.experiments.algorithm import task_skeleton

experiments = Blueprint("experiments", __name__)

@login_required
@experiments.route("/new_experiment", methods=["GET"])
def new_experiment():

    form_e = ExperimentForm()
    form_e.dataset_list()

    form_d = DatasetForm()
       
    return render_template("experiment_form.html", form_e=form_e,
        form_d=form_d, title="New experiment")

@login_required
@experiments.route("/new_experiment/launch", methods=["POST"])
def launch_experiment():
    form_e = ExperimentForm()
    user = current_user
    exp = Experiment(user.id, form_e.alg_name.data, "DEFAULT",
        form_e.data.data, None, time(), None)
    v.db.session.add(exp)
    v.db.session.commit()
    v.q.enqueue(task_skeleton, args=(exp.to_dict(), user.to_dict()))

    return redirect(url_for("experiments.new_experiment"))

@login_required
@experiments.route("/update_dataset_list", methods=["POST"])
def update_dataset_list():
    form_e = ExperimentForm()
    form_e.dataset_list()
    return render_template("blocks/select_dataset.html", form_e=form_e)

@login_required
@experiments.route("/update_alg_list", methods=["POST"])
def change_alg():
    form_e = ExperimentForm()
    form_e.alg_list(form_e.data.alg_typ)
    return render_template("blocks/show_algorithms.html", form_e=form_e)

@login_required
@experiments.route("/new_experiment/new_dataset", methods=["POST"])
def add_new_dataset():
    form_d = DatasetForm()
    upload_folder = "ubumlaas/datasets/"+current_user.username+"/"

    if form_d.validate():
        filename = secure_filename(form_d.dataset.data.filename)
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)

        # This saves the file locally but we could actually just read it and remove it
        form_d.dataset.data.save(upload_folder + filename)
        flag=True
        if filename.split(".")[-1] == "csv":
            #TODO user should define the separator
            file_df = pd.read_csv(upload_folder + filename)
        elif filename.split(".")[-1] == "xls":
            file_df = pd.read_excel(upload_folder + filename)
        else:
            flash("File format not allowed")
            flag=False
        if flag:
            file_df = pd.read_csv(upload_folder + filename)
            file_df.style.set_table_styles(
                [{'selector': 'tr:nth-of-type(odd)',
                'props': [('background', '#eee')]},
                    {'selector': 'tr:nth-of-type(even)',
                    'props': [('background', 'white')]},
                    {'selector': 'th',
                    'props': [('background', '#606060'),
                            ('color', 'white'),
                            ('font-family', 'verdana')]},
                    {'selector': 'td',
                    'props': [('font-family', 'verdana')]},
                ]
            ).hide_index()
            return render_template("blocks/show_dataset.html", data=file_df.head()
                .to_html(classes=["table-responsive", "table-borderless", "table-striped", "table-hover"]))
    else:
        return "Error", 400