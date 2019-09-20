from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField
from wtforms.fields.html5 import IntegerRangeField
from wtforms.validators import DataRequired, NumberRange
from wtforms import ValidationError
from flask_wtf.file import FileField, FileAllowed
from flask import flash
from flask_login import current_user
from ubumlaas.models import User, get_algorithms
import pandas as pd
import os


class ExperimentForm(FlaskForm):

    alg_typ = SelectField("Algorithm Type", validators=[DataRequired()],
                          choices=[("", "---"), ("Regression", "Regression"), ("Classification", "Classification")])

    alg_name = SelectField("Algorithm Name", validators=[DataRequired()],
                           choices=[])

    data = SelectField("Dataset", validators=[DataRequired()],
                       choices=[("","---")])

    def alg_list(self, alg_typ):
        self.alg_name.choices = [(x.alg_name, x.web_name)
                                 for x in get_algorithms(alg_typ)]

    def dataset_list(self):
        if os.path.isdir("ubumlaas/datasets/"+current_user.username):
            self.data.choices = [("","---")]+[(x, x) for x in os.listdir(
                "ubumlaas/datasets/"+current_user.username)]

    submit = SubmitField("Create")


class DatasetForm(FlaskForm):
    dataset = FileField()
    def to_dataframe(self, filename, upload_folder):
        if filename.split(".")[-1] == "csv":
            file_df = pd.read_csv(upload_folder + filename)
        elif filename.split(".")[-1] == "xls":
            file_df = pd.read_excel(upload_folder + filename)
        else:
            flash("File format not allowed")
        return file_df

class DatasetParametersForm(FlaskForm):
    separator = SelectField("Column separator", validators=[DataRequired()], choices=[("column", ":"), ("semicolon", ";"), ("tab", "tab"), ("comma", ",")])
    train_partition = IntegerRangeField("Train/Test partition", validators=[NumberRange(0,100)])

class DatasetTargetForm(FlaskForm):
    target_column = SelectField("Target column", validators=[DataRequired()], choices=[])

    def add_target_candidates(self, columns):
        self.target_column.choices = [(x,x) for x in columns]