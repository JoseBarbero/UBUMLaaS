from flask import render_template, url_for, flash, redirect, request, Blueprint, abort
from flask_login import login_user, current_user, logout_user, login_required
import variables as v
from ubumlaas.users.forms import RegistrationForm, LoginForm, PasswordForm, EmailForm
from ubumlaas.models import User, get_experiments
import os
from ubumlaas.util import generate_confirmation_token, confirm_token, send_email, get_ngrok_url

users = Blueprint("users", __name__)

@users.route("/login", methods=["GET", "POST"])
def login():
    """User login.

    Returns:
        string -- redirect new page
    """
    if current_user.is_authenticated:
        return redirect(url_for('core.index'))
    form = LoginForm()

    if request.method == "POST":
        go_to = url_for("users.login")
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user is not None and user.check_password(form.password.data):
                login_user(user)
                go_to = url_for("core.index")
            else:
                flash("Wrong username or password", "danger")
        else:
            flash("Wrong username or password", "danger")
        return redirect(go_to)

    return render_template("login.html", form=form, title="Log in")


@users.route("/register", methods=["GET", "POST"])
def register():
    """User registry.

    Returns:
        string -- render register or redirect log in.
    """
    if current_user.is_authenticated:
        return redirect(url_for('core.index'))

    form = RegistrationForm()

    if form.validate_on_submit():
        if form.email_exists(form.email):
            flash("Email already exists", "warning")
        elif form.username_exists(form.username):
            flash("Username already exists", "warning")
        else:
            user = User(email=form.email.data,
                        username=form.username.data,
                        password=form.password.data)
            v.db.session.add(user)
            
            default_datasets(form.username.data)
            flash("User registered.", "success")
            token = generate_confirmation_token(user.email)
            confirm_url = get_ngrok_url('users.confirm_email', token = token)
            html = render_template('confirm.html', confirm_url=confirm_url)
            subject = "Please confirm your email"
            send_email(subject, user.email, html=html)

            flash('A confirmation email has been sent via email. Please confirm email before login.', 'success')
            v.db.session.commit()
            return redirect(url_for("users.login"))
    return render_template("register.html", form=form, title="Register",
                           password_msg=form.password_msg)


def default_datasets(username):
    _dest = "ubumlaas/datasets/"+username+"/"
    _from = "ubumlaas/default_datasets/"
    try:
        os.makedirs(_dest)
        for d in os.listdir(_from):
            os.link(_from+d, _dest+d)
    except OSError:
        pass   


@users.route("/logout")
def logout():
    """User log out.

    Returns:
        string -- redirect to index.
    """
    logout_user()
    return redirect(url_for("core.index"))



@users.route("/profile")
@login_required
def profile():
    """User profile load.

    Returns:
        string -- render profile page.
    """
    datasets = [x for x in
                os.listdir("ubumlaas/datasets/"+current_user.username)]
    experiments = get_experiments(current_user.id)
    return render_template("profile.html",
                           title=current_user.username + " Profile",
                           user=current_user,
                           datasets=datasets,
                           experiments=experiments)

@users.route('/confirm/<token>')
def confirm_email(token):
    email = confirm_token(token)
    if not email:
        flash('The confirmation link is invalid or has expired.', 'danger')
        return redirect(url_for("users.login"))

    user = User.query.filter_by(email=email).first_or_404()
    if user.activated:
        flash('Account already confirmed. Please login.', 'success')
    else:
        user.activated = True
        v.db.session.add(user)
        v.db.session.commit()
        flash('You have confirmed your account. Thanks!', 'success')
    return redirect(url_for('users.login'))

@users.route('/reset', methods=["GET", "POST"])
def reset():
    form = EmailForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first_or_404()

        subject = "Password reset requested"

        token = generate_confirmation_token(user.email)

        recover_url = get_ngrok_url('users.reset_with_token', token=token)

        html = render_template(
            'recover.html',
            recover_url=recover_url)

        send_email(subject, user.email, html=html)
        flash("Reset password sended to: "+user.email, "success")
        return redirect(url_for('users.login'))
    return render_template('reset.html', form=form)

@users.route('/reset/<token>', methods=["GET", "POST"])
def reset_with_token(token):
    email = confirm_token(token)
    if not email:
        abort(404)

    form = PasswordForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=email).first_or_404()

        user.set_password(form.password.data)

        v.db.session.add(user)
        v.db.session.commit()
        flash("Password changed", "success")
        return redirect(url_for('users.login'))

    return render_template('reset_with_token.html', form=form, token=token)