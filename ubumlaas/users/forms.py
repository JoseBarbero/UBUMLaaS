from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FileField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp
from wtforms import ValidationError
from flask_wtf.file import FileField, FileAllowed
from flask import flash
from flask_login import current_user
from ubumlaas.models import User

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Log in")

class RegistrationForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[Length(min=4), DataRequired(), EqualTo("confirm_password", message="Passwords must match")]) #, Regexp(regex=r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$", message="Password requirements: Minimum eight characters, at least one uppercase letter, one lowercase letter, one number and one special character")])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired()])
    submit = SubmitField("Register")

    def email_exists(self, field):
        if User.query.filter_by(email=field.data).first():
            return True
        return False

    def username_exists(self, field):
        if User.query.filter_by(username=field.data).first():
            return True
        return False
            
class DatasetForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    dataset = FileField()
    submit = SubmitField("Upload dataset")