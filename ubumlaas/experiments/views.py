from flask import \
    (render_template, url_for, flash, redirect, request, Blueprint, jsonify, send_file, abort, safe_join)
import variables as v
from ubumlaas.models import \
    (User, Experiment, load_user, load_experiment, get_algorithm_by_name)
from ubumlaas.experiments.forms import \
    (ExperimentForm, DatasetForm, DatasetParametersForm)
from flask_login import (current_user, login_required)
from flask_mail import Message
from time import time
from werkzeug.utils import secure_filename
import os
import pandas as pd
import json
from urllib.parse import unquote
import calendar
import time

from ubumlaas.experiments.algorithm import task_skeleton

experiments = Blueprint("experiments", __name__)


@login_required
@experiments.route("/new_experiment", methods=["GET"])
def new_experiment():
    """Render a empty experiment page.
    
    Returns:
        str -- HTTP response with rendered page.
    """

    form_e = ExperimentForm()
    form_e.dataset_list()

    form_d = DatasetForm()


    form_p = DatasetParametersForm()

    return render_template("experiment_form.html", form_e=form_e,
                            form_d=form_d, form_p=form_p,
                            title="New experiment")


@login_required
@experiments.route("/new_experiment/launch", methods=["POST"])
def launch_experiment():
    """Launch a configurated experiment.

    Returns:
        str -- HTTP response with redirection
    """
    user = current_user
    dataset_config = json.loads(unquote(request.form.get("dataset_config")))
    exp_config = {"type": "partition",
                  "split": int(dataset_config["train_partition"]),
                  "target": dataset_config["target"],
                  "columns": dataset_config["selected_columns"]}
    exp = Experiment(user.id, request.form.get("alg_name"),
                     unquote(request.form.get("alg_config")),
                     json.dumps(exp_config), request.form.get("data"),
                     None, time.time(), None, 0)
    v.db.session.add(exp)
    v.db.session.commit()
    v.q.enqueue(task_skeleton, args=(exp.to_dict(), user.to_dict()),
                result_ttl=0)

    return redirect(url_for("experiments.new_experiment"))

@login_required
@experiments.route("/update_dataset_list", methods=["POST"])
def update_dataset_list():
    """Update dataset list
    
    Returns:
        str -- HTTP response with rendered dataset selector
    """
    form_e = ExperimentForm()
    form_e.dataset_list()
    return render_template("blocks/select_dataset.html", form_e=form_e)


@login_required
@experiments.route("/update_alg_list", methods=["POST"])
def change_alg():
    """Update algorithm list.

    Returns:
        str -- HTTP response with rendered algorithm selector
    """
    form_e = ExperimentForm()
    form_e.alg_list(alg_typ=request.form.get("alg_typ"))
    return render_template("blocks/show_algorithms.html", form_e=form_e)


@login_required
@experiments.route("/update_column_list", methods=["POST"])
def change_column_list():
    """Render dataset form configuration and dataset head.
    
    Returns:
        str -- HTTP response with JSON
    """
    form_e = ExperimentForm()
    dataset = form_e.data.data
    upload_folder = "ubumlaas/datasets/"+current_user.username+"/"
    df = pd.read_csv(upload_folder+dataset)
    pretty_df = generate_df_html(df)
    to_return = {"html": render_template("blocks/show_columns.html", data=df),
                 "df": generate_df_html(df)}
    return jsonify(to_return)


@login_required
@experiments.route("/new_experiment/new_dataset", methods=["POST"])
def add_new_dataset():
    """Uploads a new dataset and displays it as html table.

    Returns:
        str -- HTTP response 200 if dataset is upload or 400  if failed.
    """
    form_d = DatasetForm()
    upload_folder = "ubumlaas/datasets/"+current_user.username+"/"

    if form_d.validate():
        filename = secure_filename(form_d.dataset.data.filename)
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)

        exists = os.path.exists(upload_folder + filename)
        if(exists):
            basename, ext = os.path.splitext(os.path.basename(filename))

            filename = basename+"-"+str(calendar.timegm(time.gmtime()))+ext

        form_d.dataset.data.save(upload_folder + filename)

        file_df = form_d.to_dataframe(filename, upload_folder)

        df_html = generate_df_html(file_df)
        return render_template("blocks/show_dataset.html", data=df_html,
                               exists=exists, name=filename)
    else:
        return "Error", 400

def generate_df_html(df):
    """Generates an html table from a dataframe.
    
    Arguments:
        df {dataframe} -- pandas dataframe with dataset
    
    Returns:
        str -- html dataframe
    """
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
                    'props': [('font-family', 'verdana')]}]
        ).hide_index()
    html_table = df.to_html(classes=["table", "table-borderless", "table-striped", "table-hover"], col_space="100px", max_rows=6, justify="center").replace("border=\"1\"", "border=\"0\"").replace('<tr>', '<tr align="center">')
    return html_table


@login_required
@experiments.route("/experiment/<id>")
def result_experiment(id):
    """See experiment information

    Arguments:
        id {int} -- experiment identifier

    Returns:
        str -- HTTP response with rendered experiment information
    """
    exp = load_experiment(id)
    if exp.idu != current_user.id:
        return "", 403
    return render_template("result.html",experiment=exp,title="Experiment Result",dict_config=json.loads(exp.alg_config),conf=json.loads(get_algorithm_by_name(exp.alg_name).config))


@experiments.route("/experiment/form_generator", methods=["POST"])
def form_generator():
    """Get algorithm configuration to generate a form.

    Returns:
        str -- HTTP response with JSON
    """
    alg_name = request.form.get('alg_name')
    alg = get_algorithm_by_name(alg_name)
    return jsonify({"alg_config": alg.config})

@login_required
@experiments.route("/experiment/<int:id>/download_model")
def download_model(id):
    """Download model file using the experiment id
    
    Arguments:
        id int -- experiment id
    
    Returns:
        file -- model file
    """

    exp = load_experiment(id)

    if not exp or exp.idu != current_user.id:
        abort(404)
 
    path = safe_join("models/"+current_user.username+"/","{}.model".format(id))

    download_filename = "UBUMLaaS_{}_{}.model".format(id, get_algorithm_by_name(exp.alg_name).lib)
    
    try:
        return send_file(path, attachment_filename=download_filename, as_attachment=True)
    except FileNotFoundError:
        abort(404)


@login_required
@experiments.route("/experiment/<id>/predict_dataset",methods=["POST"])
def add_predict_dataset(id):
    """Uploads a new dataset and displays it as html table.

    Returns:
        str -- HTTP response 200 if dataset is upload or 400  if failed.
    """
    form_pr = DatasetForm()
    upload_folder = "/tmp/"+current_user.username+"/"

    if form_pr.validate():
        filename = secure_filename(form_pr.dataset.data.filename)
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)

        exists = os.path.exists(upload_folder + filename)
        if(exists):
            basename, ext = os.path.splitext(os.path.basename(filename))

            filename = basename+"-"+str(calendar.timegm(time.gmtime()))+ext

        form_pr.dataset.data.save(upload_folder + filename)

        file_df = form_pr.to_dataframe(filename, upload_folder)

        df_html = generate_df_html(file_df)
        return render_template("blocks/show_dataset.html", data=df_html,
                               exists=exists, name=filename)
    else:
        return "Error", 400

@login_required
@experiments.route("/experiment/<id>/predict")
def predict(id):
    form_pr = DatasetForm()

    return render_template("predict.html", form_pr=form_pr,id=id,title="Predict")




