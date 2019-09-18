from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
import variables as v
from ubumlaas.models import User
from ubumlaas.users.forms import RegistrationForm, LoginForm, DatasetForm
from flask_mail import Message
from werkzeug.utils import secure_filename
import pandas as pd
import os

users = Blueprint("users", __name__)


@users.route("/login", methods=["GET", "POST"])
def login():

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user.check_password(form.password.data) and user is not None:
            login_user(user)

            next = request.args.get("next")

            if next == None or not next[0] == "/":
                next = url_for("core.index")
            return redirect(next)
        else:
            flash("Wrong username or password")
    return render_template("login.html", form=form)


@users.route("/register", methods=["GET", "POST"])
def register():

    form = RegistrationForm()

    if form.validate_on_submit():
        if form.email_exists(form.email):
            flash("Email already exists")
        elif form.username_exists(form.username):
            flash("Username already exists")
        else:
            user = User(email=form.email.data,
                        username=form.username.data,
                        password=form.password.data)
            v.db.session.add(user)
            v.db.session.commit()

            flash("User registered.")
            return redirect(url_for("users.login"))
    return render_template("register.html", form=form)


@users.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("core.index"))


@users.route("/upload_dataset", methods=["GET", "POST"])
def new_job():

    form = DatasetForm()
    upload_folder = "ubumlaas/datasets/"+current_user.username+"/"

    if form.validate_on_submit():
        filename = secure_filename(form.dataset.data.filename)
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)

        # This saves the file locally but we could actually just read it and remove it
        form.dataset.data.save(upload_folder + filename)

        if filename.split(".")[-1] == "csv":
            #TODO user should define the separator
            file_df = pd.read_csv(upload_folder + filename)
        elif filename.split(".")[-1] == "xls":
            file_df = pd.read_excel(upload_folder + filename)
        else:
            flash("File format not allowed")
            return redirect(url_for("users.new_job"))
        file_df = pd.read_csv(upload_folder + filename)
        file_df.style.set_table_styles(
            [{'selector': 'tr:nth-of-type(odd)',
              'props': [('background', '#eee')]},
                {'selector': 'tr:nth-of-type(even)',
                 'props': [('background', 'white')]},
                {'selector': 'th',
                 'props': [('background', '#606060'),
                           ('color', 'white'),
                           ('font-family', 'verdana')]},
                {'selector': 'td',
                 'props': [('font-family', 'verdana')]},
            ]
        ).hide_index()

        return render_template("new_job.html", form=form, data=file_df.head().to_html(classes=["table-responsive", "table-borderless", "table-striped", "table-hover"]))
    return render_template("new_job.html", form=form)
