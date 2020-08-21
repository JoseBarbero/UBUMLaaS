from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField
from wtforms.fields.html5 import IntegerRangeField, IntegerField
from wtforms.validators import DataRequired, NumberRange
from wtforms import ValidationError
from flask_wtf.file import FileField, FileAllowed
from flask import flash
from flask_login import current_user
from ubumlaas.models import \
    (User, get_algorithms, get_algorithms_type, get_compatible_filters,
     get_algorithm_by_name, get_filter_by_name)
import pandas as pd
import os
from ubumlaas.util import get_dataframe_from_file
import variables as v


class ExperimentForm(FlaskForm):
    """Experiment basic form.

    Inherit:
        FlaskForm
    """

    alg_typ = SelectField("Algorithm Type", validators=[DataRequired()],
                          choices=[("", "---")] + get_algorithms_type())

    alg_name = SelectField("Algorithm Name", validators=[DataRequired()],
                           choices=[])

    data = SelectField("Select Dataset", validators=[DataRequired()],
                       choices=[("", "---")])

    filter_name = SelectField("Select Filter",
                              choices=[("", "---")])

    def alg_list(self, alg_typ):
        """Generate a list of supported algorithms by type.

        Arguments:
            alg_typ {str} -- Type of algorithm (Regression, Classification etc.)
        """
        v.app.logger.info("%d - Generatting %s algorithms", current_user.id, alg_typ)

        self.alg_name.choices = [("", "---")]+[(x.alg_name, x.web_name)
                                               for x in get_algorithms(alg_typ)]

    def dataset_list(self):
        """Generate a list of uploaded dataset by current user.
        """
        v.app.logger.info("%d - Getting user datasets", current_user.id)
        if os.path.isdir("ubumlaas/datasets/"+current_user.username):
            self.data.choices = [("", "---")]+[(x, x) for x in os.listdir(
                "ubumlaas/datasets/"+current_user.username)]

    def filter_list(self, alg_name, filter_name=None):

        v.app.logger.info("%d - Get filters for %s algorithm", current_user.id, alg_name)

        alg = get_algorithm_by_name(alg_name)
        if alg is not None:
            alg_lib = alg.lib
            if filter_name is None:
                filter_typ = None
            else:
                filter_typ = get_filter_by_name(filter_name).filter_typ
            self.filter_name.choices = [("", "---")]+[(x.filter_name, x.web_name)
                                                      for x in get_compatible_filters(alg_lib, filter_typ)]

    submit = SubmitField("Create")


class DatasetForm(FlaskForm):
    """Upload dataset form.

    Inherit:
        FlaskForm
    """
    dataset = FileField("Upload Dataset")

    def to_dataframe(self, filename, upload_folder):
        """Load a dataset in dataframe.

        Arguments:
            filename {str} -- name of dataset
            upload_folder {str} -- folder of current user dataset

        Returns:
            [type] -- [description]
        """
        try:
            file_df = get_dataframe_from_file(upload_folder, filename) #log for this form already done in this function
        except Exception:
            flash("File format not allowed")
        return file_df


class DatasetParametersForm(FlaskForm):
    """Dataset configuration with static parameters.

    Inherit:
        FlaskForm
    """

    train_partition = IntegerRangeField("Train/Test partition",
                                        default=70,
                                        validators=[NumberRange(1, 100)])
    k_folds = IntegerField("Number of folds",
                           default=2,
                           validators=[NumberRange(2)])
