from flask import \
    (render_template, url_for, redirect, request, jsonify,
     abort)
import variables as v
from ubumlaas.models import \
    (Experiment, load_experiment,
     get_algorithm_by_name)
from ubumlaas.experiments.forms import \
    (ExperimentForm, DatasetForm, DatasetParametersForm)
from flask_login import (current_user, login_required)
import time
import json
from urllib.parse import unquote
from ubumlaas.experiments.algorithm import task_skeleton
from ubumlaas.util import get_dataframe_from_file
import ubumlaas.experiments.views as views
from ubumlaas.util import (generate_df_html, get_dict_exp, get_ensem_alg_name, get_targets_columns)
import arff

@login_required
@views.experiments.route("/new_experiment", methods=["GET"])
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
@views.experiments.route("/new_experiment/launch", methods=["POST"])
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
@views.experiments.route("/update_alg_list", methods=["POST"])
def change_alg():
    """Update algorithm list.

    Returns:
        str -- HTTP response with rendered algorithm selector
    """
    form_e = ExperimentForm()
    form_e.alg_list(alg_typ=request.form.get("alg_typ"))
    return render_template("blocks/show_algorithms.html", form_e=form_e)


@login_required
@views.experiments.route("/update_column_list", methods=["POST"])
def change_column_list():
    """Render dataset form configuration and dataset head.

    Returns:
        str -- HTTP response with JSON
    """
    form_e = ExperimentForm()
    filename = form_e.data.data
    upload_folder = "ubumlaas/datasets/"+current_user.username+"/"
    df = get_dataframe_from_file(upload_folder, filename)
    to_return = {"html": render_template("blocks/show_columns.html", data=df),
                 "html2": render_template("blocks/show_columns_reduced.html",
                                          data=df.columns),
                 "df": generate_df_html(df),
                 "config": get_targets_columns(upload_folder, filename)}

    return jsonify(to_return)


@views.experiments.route("/experiment/<id>")
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
        template = v.app.jinja_env.get_template('email.html')
        return template.render(**template_info)


@login_required
@views.experiments.route("/experiment/<int:id>/reuse")
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


@views.experiments.route("/experiment/form_generator", methods=["POST"])
def form_generator():
    """Get algorithm configuration to generate a form.

    Returns:
        str -- HTTP response with JSON
    """
    alg_name = request.form.get('alg_name')
    alg = get_algorithm_by_name(alg_name)
    if alg is not None:
        to_ret = {"alg_config": alg.config}
    else:
        to_ret = {"alg_config": {}}
    return jsonify(to_ret)
