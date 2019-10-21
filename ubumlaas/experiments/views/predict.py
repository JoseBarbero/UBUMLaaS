from flask import \
    (render_template, request, 
     send_file, abort)
import variables as v
from ubumlaas.models import \
    (load_experiment,
     get_algorithm_by_name)
from ubumlaas.experiments.forms import \
    (DatasetForm)
from flask_login import (current_user, login_required)
from time import time
import os
import json
import shutil
import pickle
import datetime
from ubumlaas.experiments.execute_algortihm import Execute_meka
from ubumlaas.experiments.algorithm import execute_weka_predict
from ubumlaas.util import get_dataframe_from_file
import ubumlaas.experiments.views as views
from ubumlaas.util import generate_df_html


@login_required
@views.experiments.route("/experiment/<id>/predict")
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
@views.experiments.route("/experiment/predict", methods=['POST'])
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
@views.experiments.route("/experiment/delete_file", methods=['DELETE'])
def delete_file():
    """Delete user temporal folder

    Returns:
        "" --
    """
    upload_folder = "/tmp/"+current_user.username+"/"
    shutil.rmtree(upload_folder)
    return "", 200


@login_required
@views.experiments.route("/experiment/<name>/download_result")
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
