from flask import \
    (render_template)
from ubumlaas.experiments.forms import \
    (ExperimentForm, DatasetForm)
from flask_login import (current_user, login_required)
from time import time
from werkzeug.utils import secure_filename
import os
import calendar
import ubumlaas.experiments.views as views
from ubumlaas.util import generate_df_html


@login_required
@views.experiments.route("/update_dataset_list", methods=["POST"])
def update_dataset_list():
    """Update dataset list

    Returns:
        str -- HTTP response with rendered dataset selector
    """
    form_e = ExperimentForm()
    form_e.dataset_list()
    return render_template("blocks/select_dataset.html", form_e=form_e)


@login_required
@views.experiments.route("/new_experiment/new_dataset", methods=["POST"])
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


@views.experiments.route("/experiment/<id>/predict_dataset", methods=["POST"])
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
