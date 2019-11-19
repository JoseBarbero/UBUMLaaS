from flask import \
    (request, jsonify,
     send_file, abort, safe_join)
from ubumlaas.models import \
    (load_experiment,
     get_algorithm_by_name, get_similar_algorithms)
from flask_login import (current_user, login_required)
import ubumlaas.experiments.views as views


@login_required
@views.experiments.route("/experiment/<int:id>/download_model")
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


@views.experiments.route("/experiment/base_estimator_getter", methods=["POST"])
def base_estimator_getter():
    alg_name = request.form.get("alg_name", None)
    exp_typ = request.form.get("exp_typ", None)
    algorithm = get_similar_algorithms(alg_name, exp_typ)

    _ret = dict()
    _ret["algorithms"] = []
    for i in algorithm:
        _ret["algorithms"].append(i.to_dict())
    return jsonify(_ret)
