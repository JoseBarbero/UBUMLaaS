from flask import render_template, url_for, flash, redirect, request, Blueprint, jsonify
import variables as v
from ubumlaas.models import User, Experiment, load_user, load_experiment, get_algorithm_by_name
from ubumlaas.experiments.forms import ExperimentForm, DatasetForm, DatasetParametersForm, DatasetTargetForm
from flask_login import current_user, login_required
from flask_mail import Message
from time import time
from werkzeug.utils import secure_filename
import os
import pandas as pd
import json
from urllib.parse import unquote

from ubumlaas.experiments.algorithm import task_skeleton

experiments = Blueprint("experiments", __name__)

@login_required
@experiments.route("/new_experiment", methods=["GET"])
def new_experiment():

    form_e = ExperimentForm()
    form_e.dataset_list()

    form_d = DatasetForm()

    form_c = DatasetTargetForm()

    form_p = DatasetParametersForm()
       
    return render_template("experiment_form.html", form_e=form_e,
        form_d=form_d, form_p=form_p, form_c=form_c, title="New experiment")


@login_required
@experiments.route("/new_experiment/launch", methods=["POST"])
def launch_experiment():
    user = current_user
    exp_config = {"type": "partition",
                  "split": int(request.form.get("train_partition")),
                  "target": request.form.get("target")}
    exp = Experiment(user.id, request.form.get("alg_name"), unquote(request.form.get("alg_config")),
                     json.dumps(exp_config), request.form.get("data"),
                     None, time(), None, 0)
    v.db.session.add(exp)
    v.db.session.commit()
    v.q.enqueue(task_skeleton, args=(exp.to_dict(), user.to_dict()), result_ttl=0)

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
    form_e.alg_list(alg_typ=request.form.get("alg_typ"))
    return render_template("blocks/show_algorithms.html", form_e=form_e)

@login_required
@experiments.route("/update_column_list", methods=["POST"])
def change_column_list():
    form_e = ExperimentForm()
    form_c = DatasetTargetForm()
    dataset = form_e.data.data
    upload_folder = "ubumlaas/datasets/"+current_user.username+"/"
    df = pd.read_csv(upload_folder+dataset)
    form_c.add_target_candidates(df.columns)
    pretty_df = generate_df_head_html(df)
    to_return = {"html": render_template("blocks/show_columns.html", form_c = form_c),
                 "df": generate_df_head_html(df)}
    return jsonify(to_return)


@login_required
@experiments.route("/new_experiment/new_dataset", methods=["POST"])
def add_new_dataset():
    form_d = DatasetForm()
    upload_folder = "ubumlaas/datasets/"+current_user.username+"/"

    if form_d.validate():
        filename = secure_filename(form_d.dataset.data.filename)
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)

        form_d.dataset.data.save(upload_folder + filename)
        
        file_df = form_d.to_dataframe(filename, upload_folder)

        pretty_df = generate_df_head_html(file_df)
        
        return render_template("blocks/show_dataset.html", data=pretty_df)
    else:
        return "Error", 400

def generate_df_head_html(df):
    df.style.set_table_styles(
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

    return df.to_html(classes=["table-responsive", "table-borderless", "table-striped", "table-hover", "table-sm"], max_rows=6, justify="justify")


@login_required
@experiments.route("/experiment/<id>")
def result_experiment(id):
    exp = load_experiment(id)
    if exp.idu != current_user.id:
        return "", 403
    return render_template("result.html",experiment=exp,title="Experiment Result")

@experiments.route("/experiment/form_generator", methods=["POST"])
def form_generator():
    alg_name = request.form.get('alg_name')
    alg = get_algorithm_by_name(alg_name)
    return jsonify({"alg_config": alg.config})
