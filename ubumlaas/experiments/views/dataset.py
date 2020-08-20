from flask import \
    (render_template)
from ubumlaas.experiments.forms import \
    (ExperimentForm, DatasetForm)
from flask_login import (current_user, login_required)
import time
from werkzeug.utils import secure_filename
import os
import calendar
import ubumlaas.experiments.views as views
from ubumlaas.util import generate_df_html
import variables as v


@login_required
@views.experiments.route("/update_dataset_list", methods=["POST"])
def update_dataset_list():
    """Update dataset list

    Returns:
        str -- HTTP response with rendered dataset selector
    """
    form_e = ExperimentForm()
    form_e.dataset_list() #log inside dataset_list
    return render_template("blocks/select_dataset.html", form_e=form_e)


@login_required
@views.experiments.route("/new_experiment/new_dataset", methods=["POST"])
def add_new_dataset():
    """Uploads a new dataset and displays it as html table.

    Returns:
        str -- HTTP response 200 if dataset is upload or 400  if failed.
    """
    return upload_dataset("ubumlaas/datasets/")


@views.experiments.route("/experiment/<id>/predict_dataset", methods=["POST"])
def add_predict_dataset(id):
    """Uploads a new dataset and displays it as html table.

    Returns:
        str -- HTTP response 200 if dataset is upload or 400  if failed.
    """
    return upload_dataset("/tmp/")


def upload_dataset(base_folder):
    form_d = DatasetForm()
    upload_folder = base_folder+current_user.username+"/"
    v.app.logger.info("%d - Uploading new dataset", current_user.id)
    v.app.logger.debug("%d - upload_folder path - %s", current_user.id, upload_folder)

    if form_d.validate():
        filename = secure_filename(form_d.dataset.data.filename)
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
            v.app.logger.debug("%d - mkdir upload_folder - %s", current_user.id, upload_folder)

        filename, exists = check_exists(upload_folder, filename)

        form_d.dataset.data.save(upload_folder + filename)

        file_df = form_d.to_dataframe(filename, upload_folder)

        df_html = generate_df_html(file_df)
        v.app.logger.info("%d - Dataset valid and rendering show_dataset block", current_user.id)
        return render_template("blocks/show_dataset.html", data=df_html,
                               exists=exists, name=filename)
    else:
        v.app.logger.warn("%d - Form for upload dataset not validated ERROR 400", current_user.id)
        return "Error", 400


def check_exists(upload_folder, filename):
    exists = os.path.exists(upload_folder + filename)
    if(exists):
        basename, ext = os.path.splitext(os.path.basename(filename))

        filename = basename+"-"+str(calendar.timegm(time.gmtime()))+ext

    return filename, exists
