from flask import \
    (render_template, url_for, redirect, request, jsonify,
     abort)
import variables as v
from ubumlaas.models import \
    (Experiment, load_experiment,
     get_algorithm_by_name, get_filter_by_name)
from ubumlaas.experiments.forms import \
    (ExperimentForm, DatasetForm, DatasetParametersForm)
from flask_login import (current_user, login_required)
import time
import json
from urllib.parse import unquote
from ubumlaas.experiments.algorithm import task_skeleton
from ubumlaas.util import get_dataframe_from_file
import ubumlaas.experiments.views as views
from ubumlaas.util import (generate_df_html, get_dict_exp, get_ensem_alg_name)
import arff
import os


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
    filter_name = request.form.get("filter_name")
    if filter_name is None or filter_name == "":
        filter_name = None
        filter_config = None
    else:
        filter_config = request.form.get("filter_config")
    exp = Experiment(user.id, request.form.get("alg_name"),
                     unquote(request.form.get("alg_config")),
                     json.dumps(exp_config),
                     filter_name, filter_config,
                     request.form.get("data"),
                     None, time.time(), None, 0)
    v.db.session.add(exp)
    v.db.session.commit()
    v.q.enqueue(task_skeleton, args=(exp.to_dict(), user.to_dict()),
                result_ttl=0)

    return redirect(url_for("experiments.new_experiment", _scheme=v.scheme))


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
    df, target_columns = get_dataframe_from_file(upload_folder, filename, target_column=True)
    to_return = {"html": render_template("blocks/show_columns.html", data=df),
                 "html2": render_template("blocks/show_columns_reduced.html",
                                          data=df.columns),
                 "df": generate_df_html(df),
                 "config": target_columns}

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
        template = v.app.jinja_env.get_template('email.html', external_url = os.getenv("NGROK_URL", "http://localhost"))
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
    alg_name = request.form.get('name')
    alg = get_algorithm_by_name(alg_name)
    if alg is not None:
        to_ret = {"config": alg.config}
        code = 200
    else:
        to_ret = {"config": {}}
        code = 418
    return jsonify(to_ret), code


@views.experiments.route("/experiment/get_filters", methods=["POST"])
def get_filters():
    """Get filters compatible

    Returns:
        str -- HTTP response with rendered filter selectable
        str -- HTTP JSON/response with list of filters
    """
    form_e = ExperimentForm()
    alg_name = request.form.get("alg_name")
    filter_name = request.form.get("filter_name", None)
    form_e.filter_list(alg_name, filter_name)
    if filter_name is None:
        return render_template("blocks/show_filters.html", form_e=form_e)
    else:
        return jsonify(dict(form_e.filter_name.choices))


@views.experiments.route("/experiment/filters_generator_form", methods=["POST"])
def form_generator_for_filter():
    filter_name = request.form.get('name')
    filter_ = get_filter_by_name(filter_name)
    if filter_ is not None:
        to_ret = {"config": filter_.config}
        code = 200
    else:
        to_ret = {"config": {}}
        code = 418
    return jsonify(to_ret), code
