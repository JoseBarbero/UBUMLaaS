from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField
from wtforms.validators import DataRequired
from wtforms import ValidationError
from flask_wtf.file import FileField, FileAllowed
from flask import flash
from flask_login import current_user
from ubumlaas.models import User
import os

class ExperimentForm(FlaskForm):

    alg_name = SelectField("Algorithm Name", validators=[DataRequired()], 
        choices=[("sklearn.linear_model.LinearRegression", "Linear Regresion"),
            ("sklearn.linear_model.LogisticRegression", "Logisitc Regresion")])

    data = SelectField("Dataset", validators=[DataRequired()], 
        choices=[])

    def dataset_list(self):
        if os.path.isdir("ubumlaas/datasets/"+current_user.username):
            self.data.choices = [(x, x) for x in os.listdir("ubumlaas/datasets/"+current_user.username)]

    submit = SubmitField("Create")


class DatasetForm(FlaskForm):
    dataset = FileField()