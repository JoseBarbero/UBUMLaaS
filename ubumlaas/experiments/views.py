from flask import \
    (render_template, url_for, redirect, request, Blueprint, jsonify,
     send_file, abort, safe_join)
import variables as v
from ubumlaas.models import \
    (Experiment, load_experiment,
     get_algorithm_by_name, get_similar_algorithms)
from ubumlaas.experiments.forms import \
    (ExperimentForm, DatasetForm, DatasetParametersForm)
from flask_login import (current_user, login_required)
from time import time
from werkzeug.utils import secure_filename
import os
import json
from urllib.parse import unquote
import calendar
import shutil
import time
import pickle
import datetime
from ubumlaas.experiments.execute_algortihm import Execute_meka
import copy
from ubumlaas.experiments.algorithm import task_skeleton, execute_weka_predict
from ubumlaas.util import get_dataframe_from_file
from jinja2 import Environment, PackageLoader, select_autoescape

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

    exp = request.args.get("exp", None)
    experiment = None
    if exp is not None:
        experiment = load_experiment(exp).to_dict()

    return render_template("experiment_form.html", form_e=form_e,
                           form_d=form_d, form_p=form_p,
                           title="New experiment", experiment=experiment)


@login_required
@experiments.route("/new_experiment/launch", methods=["POST"])
def launch_experiment():
    """Launch a configurated experiment.

    Returns:
        str -- HTTP response with redirection
    """
    user = current_user
    dataset_config = json.loads(unquote(request.form.get("dataset_config")))
    exp_config = dataset_config
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
    df = get_dataframe_from_file(upload_folder, dataset)
    to_return = {"html": render_template("blocks/show_columns.html", data=df),
                 "html2": render_template("blocks/show_columns_reduced.html", data=df.columns),
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


def generate_df_html(df, num=6):

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
    html_table = df.to_html(classes=["table", "table-borderless",
                                     "table-striped", "table-hover"],
                            col_space="100px", max_rows=num, justify="center")\
                   .replace("border=\"1\"", "border=\"0\"") \
                   .replace('<tr>',
                            '<tr align="center">')
    return html_table


@experiments.route("/experiment/<id>")
def result_experiment(id, admin=False):
    """See experiment information

    Arguments:
        id {int} -- experiment identifier
        admin {boolean} -- administration petition.
                           If True current user doesn't matters.

    Returns:
        str -- HTTP response with rendered experiment information
    """
    exp = load_experiment(id)
    if not admin and exp.idu != current_user.id:
        return "", 403
    name = exp.alg_name
    dict_config = json.loads(exp.alg_config)
    if "base_estimator" in dict_config.keys():
        name += "-" + get_ensem_alg_name(dict_config["base_estimator"])
    dict_config = get_dict_exp(exp.alg_name, dict_config)
    template_info = {"experiment": exp,
                     "name": name,
                     "title": "Experiment Result",
                     "dict_config": dict_config,
                     "conf": json.loads(get_algorithm_by_name(
                                        exp.alg_name).config)}
    if not admin:
        return render_template("result.html", **template_info)
    else:
        template_info["experiment"].result = \
            json.loads(template_info["experiment"].result)
        template = v.app.jinja_env.get_template('email.html')
        return template.render(**template_info)


def get_ensem_alg_name(conf):
    if "base_estimator" in conf["parameters"].keys():
        return conf["alg_name"] + "-" + get_ensem_alg_name(
            conf["parameters"]["base_estimator"])
    else:
        return conf["alg_name"]


def get_dict_exp(name, dict_config):
    cd = copy.deepcopy(dict_config)
    d = {name: cd}
    if "base_estimator" in dict_config.keys():
        del d[name]["base_estimator"]
        d[name]["base_estimator"] = dict_config["base_estimator"]["alg_name"]
        name += dict_config["base_estimator"]["alg_name"]
        d.update(get_dict_exp(name,
                              dict_config["base_estimator"]["parameters"]))
        return d
    else:
        return d


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

    path = safe_join("models/"+current_user.username+"/", "{}.model"
                                                          .format(id))

    download_filename = "UBUMLaaS_{}_{}.model" \
                        .format(id, get_algorithm_by_name(exp.alg_name).lib)

    try:
        return send_file(path, attachment_filename=download_filename,
                         as_attachment=True)
    except FileNotFoundError:
        abort(404)


@login_required
@experiments.route("/experiment/<int:id>/reuse")
def reuse_experiment(id):
    exp = load_experiment(id)

    if not exp or exp.idu != current_user.id:
        abort(404)

    form_e = ExperimentForm()

    form_e.dataset_list()
    form_e.process()

    form_d = DatasetForm()

    form_p = DatasetParametersForm()

    return render_template("experiment_form.html", form_e=form_e,
                           form_d=form_d, form_p=form_p,
                           title="New experiment")


@experiments.route("/experiment/base_estimator_getter", methods=["POST"])
def base_estimator_getter():
    alg_name = request.form.get("alg_name", None)
    algorithm = get_similar_algorithms(alg_name)

    _ret = dict()
    _ret["algorithms"] = []
    for i in algorithm:
        _ret["algorithms"].append(i.to_dict())
    return jsonify(_ret)


@experiments.route("/experiment/<id>/predict_dataset", methods=["POST"])
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
    """Render predict html.

    Arguments:
        id {int} -- experiment identificator.

    Returns:
        str -- render predict html.
    """
    form_pr = DatasetForm()

    return render_template("predict.html", form_pr=form_pr,
                           id=id, title="Predict")


@login_required
@experiments.route("/experiment/predict", methods=['POST'])
def start_predict():
    """Start prediction

    Returns:
        [type] -- [description]
    """
    exp_id = request.form.get('exp_id')
    filename = request.form.get('filename')
    upload_folder = "/tmp/"+current_user.username+"/"
    fil_name = "predict_" + exp_id + "-" + \
               datetime.datetime.now().strftime("%d_%m_%Y-%H_%M_%S")+".csv"

    exp = load_experiment(exp_id)

    alg = get_algorithm_by_name(exp.alg_name)
    path = "ubumlaas/models/" + current_user.username + \
           "/"+"{}.model".format(exp_id)
    if alg.lib == "sklearn":
        # Open experiment configuration
        exp_config = json.loads(exp.exp_config)

        file_df = get_dataframe_from_file(upload_folder, filename)
        prediction_df = file_df[exp_config["columns"]]

        model = pickle.load(open(path, 'rb'))
        predictions = model.predict(prediction_df)
        if exp_config["target"] in file_df:
            prediction_df[exp_config["target"]] = file_df[exp_config["target"]]
        prediction_df["prediction_"+exp_config["target"]] = predictions

        delete_file()
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
        prediction_df.to_csv(upload_folder + fil_name, index=None)

    elif alg.lib == "weka":
        job = v.q.enqueue(execute_weka_predict,
                          args=(current_user.username,
                                exp_id,
                                filename,
                                path,
                                fil_name)
                          )
        while job.result is None:
            time.sleep(2)
        if job.result is False:
            return "", 400
        prediction_df = get_dataframe_from_file(upload_folder, fil_name)

    elif alg.lib == "meka":
        exp_config = json.loads(exp.exp_config)
        meka = Execute_meka(exp.to_dict())
        model_meka = meka.deserialize(path)
        X, y = meka.open_dataset(upload_folder, filename)
        prediction_df, _ = meka.predict(model_meka, X, y)

        delete_file()
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
        prediction_df.to_csv(upload_folder + fil_name, index=None)

    else:
        return "", 400

    df_html = generate_df_html(prediction_df, num=None)
    return render_template("blocks/predict_result.html",
                           data=df_html,
                           file=fil_name)


@login_required
@experiments.route("/experiment/delete_file", methods=['DELETE'])
def delete_file():
    """Delete user temporal folder

    Returns:
        "" --
    """
    upload_folder = "/tmp/"+current_user.username+"/"
    shutil.rmtree(upload_folder)
    return "", 200


@login_required
@experiments.route("/experiment/<name>/download_result")
def download_result(name):
    """Download csv file with prediction

    Arguments:
        name {str} -- csv file name

    Returns:
        send file -- download file
    """
    upload_folder = "/tmp/"+current_user.username+"/"
    try:
        return send_file(upload_folder+name, attachment_filename=name,
                         as_attachment=True)
    except FileNotFoundError:
        abort(404)
