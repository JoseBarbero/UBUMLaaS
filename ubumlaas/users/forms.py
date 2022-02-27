from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp, AnyOf
from ubumlaas.models import User
import pycountry

class CountrySelectField(SelectField):
    def __init__(self, *args, **kwargs):
        super(CountrySelectField, self).__init__(*args, **kwargs)
        self.choices = [(country.alpha_2, country.name)
                        for country in pycountry.countries]

password_msg_global = "Password requirements: Minimum eight characters, at least one uppercase letter, one lowercase letter, one number and one special character => @$!%*?&().="
email_field =  StringField("Email", validators=[DataRequired(), Email()])
password_field = PasswordField("Password", validators=[Length(min=4), DataRequired(), EqualTo("confirm_password", message="Passwords must match"), Regexp(regex=r"(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[$@$!%*?&\(\)=\.\,])([A-Za-z\d$@$!%*?&\(\)=\.\,]|[^ ]){8,}$", message=password_msg_global)])
confirm_password_field = PasswordField("Confirm Password", validators=[DataRequired()])
country_field = CountrySelectField()
desired_use_filed = SelectField("Desired use", choices=["Education", "Professional Work", "Research"],
    validators=[AnyOf(values=["Education", "Professional Work", "Research"])])

class LoginForm(FlaskForm):
    """Form for the log in.

    Inherit:
        FlaskForm {[FlaskForm]} -- Flask-specific subclass of WTForms.
    """
    email = email_field
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Log in")


class RegistrationForm(FlaskForm):
    """Form for registration of an user.

    Inherit:
        FlaskForm {[FlaskForm]} -- Flask-specific subclass of WTForms.
    """
    password_msg = password_msg_global
    email = StringField("Email", validators=[DataRequired(), Email()])
    username = StringField("Username", validators=[DataRequired()])
    password = password_field
    confirm_password = confirm_password_field
    country = country_field
    desired_use = desired_use_filed
    website = StringField('Personal Website')
    twitter = StringField('Twitter username')
    github = StringField('GitHub username')
    institution = StringField('Institution')
    linkedin = StringField('LinkedIn username')
    google_scholar = StringField('Google Scholar URL')
    update_checkbox = BooleanField('Update user data')

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

class EmailForm(FlaskForm):
    email = email_field
    submit = SubmitField("Send")

class PasswordForm(FlaskForm):
    pass_checkbox = BooleanField('Update Password')
    password_msg = password_msg_global
    password = password_field
    confirm_password = confirm_password_field
    submit = SubmitField("Reset password")
