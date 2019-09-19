from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField
from wtforms.validators import DataRequired
from wtforms import ValidationError
from flask_wtf.file import FileField, FileAllowed
from flask import flash
from flask_login import current_user
from ubumlaas.models import User,get_algorithms
import os

class ExperimentForm(FlaskForm):

    alg_typ = SelectField("Algorithm Type", validators=[DataRequired()],
        choices=[("Regression","Regression"),("Classification","Classification")])

    alg_name = SelectField("Algorithm Name", validators=[DataRequired()], 
        choices=[])

    data = SelectField("Dataset", validators=[DataRequired()], 
        choices=[])

    def alg_list(self,alg_typ):
        self.alg_name.choices = [(x.alg_name, x.web_name) for x in get_algorithms(alg_typ)]

    def dataset_list(self):
        if os.path.isdir("ubumlaas/datasets/"+current_user.username):
            self.data.choices = [(x, x) for x in os.listdir("ubumlaas/datasets/"+current_user.username)]

    submit = SubmitField("Create")


class DatasetForm(FlaskForm):
    dataset = FileField()