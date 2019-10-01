from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
import variables as v
from ubumlaas.models import User
from ubumlaas.users.forms import RegistrationForm, LoginForm
from flask_mail import Message
import smtplib

users = Blueprint("users", __name__)

EMAIL_AC = 'ubumlaas@gmail.com'
EMAIL_PASS = 'rotationforest'

@users.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('core.index'))
    form = LoginForm()
    if request.method == "POST":
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user is not None and user.check_password(form.password.data):
                login_user(user)

                next = request.args.get("next")

                if next == None or not next[0] == "/":
                    next = url_for("core.index")
                return redirect(next)
        flash("Wrong username or password")
        return redirect(url_for("users.login"))

    return render_template("login.html", form=form, title="Log in")


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
    return render_template("register.html", form=form, title="Register")


@users.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("core.index"))


@login_required
@users.route("/profile")
def profile():
    datasets = [x for x in os.listdir("ubumlaas/datasets/"+current_user.username)]
    experiments = get_experiments(current_user.id)
    return render_template("profile.html", title= current_user.username + " Profile", user=current_user, datasets=datasets, experiments=experiments)

  
def send_email(user, email, procid):
    with smtplib.SMTP('smtp.gmail.com',587) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()

        smtp.login(EMAIL_AC,EMAIL_PASS)

        subject= 'Your process on UBUMLaaS' + str(procid) + ' has finished.'

        body = 'Hi ' + user + ', your process ' + procid + ', that were running on UBUMLaaS has finished.'

        msg = f'Subject: {subject}\n\n{body}'

        smtp.sendmail(EMAIL_AC, email ,msg)
    return redirect(url_for("core.index"))
