from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp
from ubumlaas.models import User


class LoginForm(FlaskForm):
    """Form for the log in.

    Inherit:
        FlaskForm {[FlaskForm]} -- Flask-specific subclass of WTForms.
    """
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Log in")


class RegistrationForm(FlaskForm):
    """Form for registration of an user.

    Inherit:
        FlaskForm {[FlaskForm]} -- Flask-specific subclass of WTForms.
    """
    email = StringField("Email", validators=[DataRequired(), Email()])
    username = StringField("Username", validators=[DataRequired()])
    password_msg = "Password requirements: Minimum eight characters, at least one uppercase letter, one lowercase letter, one number and one special character => @$!%*?&().="
    password = PasswordField("Password", validators=[Length(min=4), DataRequired(), EqualTo("confirm_password", message="Passwords must match"), Regexp(regex=r"(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[$@$!%*?&\(\)=\.\,])([A-Za-z\d$@$!%*?&\(\)=\.\,]|[^ ]){8,}$", message=password_msg)])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired()])
    submit = SubmitField("Register")

    def email_exists(self, field):
        """Validate if email exists or not

        Arguments:
            field {input} -- email.

        Returns:
            bool -- true if email exists, false if not.
        """
        if User.query.filter_by(email=field.data).first():
            return True
        return False

    def username_exists(self, field):
        """Validate if username exists or not

        Arguments:
            field {input} -- username.

        Returns:
            bool -- true if username exists, false if not.
        """
        if User.query.filter_by(username=field.data).first():
            return True
        return False
