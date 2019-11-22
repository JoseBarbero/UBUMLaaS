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
from time import time,sleep
import os
import shutil
import datetime
from ubumlaas.experiments.algorithm import execute_weka_predict
from ubumlaas.util import get_dataframe_from_file
import ubumlaas.experiments.views as views
from ubumlaas.util import generate_df_html
import pandas as pd


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

    exp = load_experiment(exp_id)

    if not exp or exp.idu != current_user.id:
        abort(404)

    upload_folder = "/tmp/"+current_user.username+"/"
    prediction_filename = "predict_"+exp_id+"-" + datetime.datetime.now().strftime("%d_%m_%Y-%H_%M_%S")+".csv"

    alg = get_algorithm_by_name(exp.alg_name)
    path = "ubumlaas/models/{}/{}.model".format(current_user.username, exp_id)
    exp = exp.to_dict()
    if alg.lib == "sklearn" or alg.lib == "meka":
        # Open experiment configuration
        execute = v.apps_functions[alg.lib](exp)

        exp_config = execute.experiment_configuration

        # Open to predict dataset
        file_df, y = execute.open_dataset(upload_folder, filename)
        prediction_df = file_df[exp_config["columns"]]

        model = execute.deserialize(path)
        predictions, _ = execute.predict(model, file_df)
        columns = [prediction_df]
        if y is not None:
            y_df = pd.DataFrame(y, columns=exp_config["target"])
            columns.append(y_df)

        predictions_columns = ["prediction_"+target_name for target_name in exp_config["target"]] if exp_config["target"] else ["clusters_"+datetime.datetime.now().strftime("%d_%m_%Y-%H_%M_%S")]
        pred_df = pd.DataFrame(predictions, columns=predictions_columns)
        columns.append(pred_df)
        prediction_df = pd.concat(columns, axis = 1)

        delete_file()
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
        prediction_df.to_csv(upload_folder + prediction_filename, index=None)

    elif alg.lib == "weka":
        job = v.q.enqueue(execute_weka_predict,
                          args=(current_user.username,
                                exp,
                                filename,
                                path,
                                prediction_filename)
                          )
        while job.result is None:
            sleep(2)
        if job.result is False:
            return "", 400
        prediction_df = get_dataframe_from_file(upload_folder, prediction_filename)
        pred_df=prediction_df.iloc[:, -1].to_frame()

    else:
        return "", 400

    df_html = generate_df_html(prediction_df, num=None)
    pred_html=generate_df_html(pred_df,num=None)
    return render_template("blocks/predict_result.html",
                           data=df_html,
                           datareduc=pred_html,
                           file=prediction_filename)


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
