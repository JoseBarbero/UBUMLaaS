from flask import render_template, Blueprint, send_from_directory, request, jsonify, flash
from flask_wtf import FlaskForm
from flask_login import login_required, current_user
from wtforms import SelectField
from ubumlaas.models import User, Country, Experiment
from ubumlaas.users.forms import RegistrationForm
from ubumlaas.util import generate_confirmation_token, confirm_token, send_email, get_ngrok_url
from ._utils import is_admin, get_users_info, geolocate
from sqlalchemy import text, select
from datetime import datetime, date
import time
import os
import variables as v
import uuid
import folium
import pandas as pd
import numpy as np

admin = Blueprint('admin', __name__)

@admin.route('/administration')
@login_required
def administration():
    is_admin()
    return render_template(
        'admin/administration.html', 
        current_user=current_user, 
        ip=request.environ.get('HTTP_X_REAL_IP', request.remote_addr),
        title="Administration")

@admin.route('/administration/users', methods=["GET", "POST"])
@login_required
def admin_users():
    is_admin()
    users_info = get_users_info()

    admin_form = RegistrationForm()
    admin_form.password.data = "!1HoLaGg"
    admin_form.confirm_password.data = "!1HoLaGg"
    
    if admin_form.validate_on_submit():
        if admin_form.email_exists(admin_form.email):
            flash("Email already exists", "warning")
            v.app.logger.info(
                "-1 - Trying to register with an email that already exists, %s", admin_form.email.data)
        elif admin_form.username_exists(admin_form.username):
            flash("Username already exists", "warning")
            v.app.logger.info(
                "-1 - Trying to register with an username that already exists, %s", admin_form.username.data)
        else:
            user = User(email=admin_form.email.data,
                        username=admin_form.username.data,
                        password=str(uuid.uuid4()),
                        desired_use=admin_form.desired_use.data,
                        country=admin_form.country.data,
                        activated=0,
                        user_type=1)
            v.db.session.add(user)

            default_datasets(admin_form.username.data)
            flash("User registered.", "success")
            token = generate_confirmation_token(user.email)
            confirm_url = get_ngrok_url('users.confirm_email', token=token)

            subject = "Please confirm your email"
            html = render_template('confirm.html', confirm_url=confirm_url)
            send_email(subject, user.email, html=html)

            v.app.logger.info("%d - User registered", user.id)
            v.db.session.commit()
            return render_template('admin/admin_users.html',
                                  ip=request.environ.get(
                                      'HTTP_X_REAL_IP', request.remote_addr),
                                  current_user=current_user,
                                   all_users=get_users_info(),
                                   form=admin_form,
                                  title="Users Administration")

    return render_template('admin/admin_users.html',
                           ip=request.environ.get(
                           'HTTP_X_REAL_IP', request.remote_addr),
                           current_user=current_user,
                           all_users=users_info,
                           form=admin_form,
                           title="Users Administration")

@admin.route('/administration/activate', methods=["GET"])
@login_required
def activate_user():
    is_admin()
    if request.method == "GET":
        id = request.args.get('id')
        option = request.args.get('option')
        
        try:
            if option == "True":
                User.query.filter_by(id=id).update(
                    {'activated': 0}, synchronize_session=False)
                v.db.session.commit()
                flash("User deactivated", "success")
                v.app.logger.info('User %d - is deactivated', id)
            else:
                User.query.filter_by(id=id).update(
                    {'activated': 1}, synchronize_session=False)
                v.db.session.commit()
                flash("User activated", "success")
                v.app.logger.info('User %d - is activated', id)
        except Exception as ex:
            v.app.logger.exception(str(ex))
            v.db.session.rollback()
            flash("Failed to update user status", "error")
            raise Exception('Failed to update DB')
        return 'ok'
    else:
        raise Exception('Failed to update DB')
    
@admin.route('/admonistration/admin', methods=["GET"])
@login_required
def user_to_admin():
    is_admin()
    if request.method == "GET":
        id = request.args.get('id')
        if str(id) == str(current_user.id):
            v.app.logger.info('User %d - can not make himself not admin', id)
            raise Exception('Can not unmake yourself as admin')
        option = request.args.get('option')

        try:
            if option == '1':
                User.query.filter_by(id=id).update(
                    {'user_type': 0}, synchronize_session=False)
                v.db.session.commit()
                flash("User is now admin", "success")
                v.app.logger.info('User %d - is now admin', id)
            else:
                User.query.filter_by(id=id).update(
                    {'user_type': 1}, synchronize_session=False)
                v.db.session.commit()
                flash("User is no longer admin", "success")
                v.app.logger.info('User %d - is no longer admin', id)
        except Exception as ex:
            v.app.logger.exception(str(ex))
            v.db.session.rollback()
            flash("Failed to update user status", "error")
            raise Exception('Failed to update DB')
        return 'ok'
    else:
        v.app.logger.info('Failed to update DB')
        raise Exception('Failed to update DB')

@admin.route('/administration/delete', methods=["GET"])
@login_required
def del_user():
    is_admin()
    if request.method == "GET":
        id = request.args.get('id')
        try:
            v.app.logger.info("Deleting user with id %d", id)
            User.query.filter_by(id=id).delete()
            v.db.session.commit()
            flash("User deleted", "success")
        except Exception as ex:
            flash("Failed to delete user", "success")
            v.app.logger.exception(str(ex))
            v.db.session.rollback()
        return 'ok'
    else:
        v.app.logger.info("Failed to delete user with id %d", id)
        raise Exception('Failed to delete user.')

def default_datasets(username):
    _dest = "ubumlaas/datasets/"+username+"/"
    _from = "ubumlaas/default_datasets/"
    try:
        os.makedirs(_dest)
        for d in os.listdir(_from):
            os.link(_from+d, _dest+d)
    except OSError:
        pass

@admin.route('/administration/dashboard')
@login_required
def dashboard():
    is_admin()
    unique = {}
    map = folium.Map(zoom_level=0, tiles='CartoDB positron')
    
    users_info = get_users_info()
    countries_alpha_2 = [user['country'] for user in users_info]
    unique_alpha_2 = {}
    for country in countries_alpha_2:
        try:
            unique_alpha_2[country] += 1
        except KeyError:
            unique_alpha_2[country] = 1

    for u, t in unique_alpha_2.items():
        try:
            unique[u] = Country.query.filter_by(alpha_2=u).first().to_dict()
            popup = folium.Popup('{}: {} user/s'.format(unique[u]['name'], t), max_width=450)
            folium.Marker([unique[u]['latitude'], unique[u]['longitude']], 
                popup=popup).add_to(map)
        except Exception:
            v.app.logger.info("%d - Country not found in db: %s", current_user.id, u)
    
    unique_datasets = set([f for dp, dn, fn in os.walk(
        os.path.expanduser("ubumlaas/datasets/")) for f in fn])
    
    all_experiments = Experiment.query.all()
    dict_experiments = {}
    exps_7d_df = pd.DataFrame([[f'I-{x}', 0] for x in range(7)],columns=['day', 'times'])
    experiments_df = pd.DataFrame(columns=['dataset', 'times'])
    today = time.localtime(time.time())[:3]

    for e in all_experiments:
        e = e.to_dict()
        endtime = np.array([x for x in datetime.fromtimestamp(e['endtime']).strftime("%Y-%m-%d_%H:%M:%S").strip().split('_')[0].split('-')]).astype(int)
        delta = date(*today) - date(*endtime)
        print(today, endtime, delta.days)
        if delta.days < 7:
            exps_7d_df.at[delta.days, 'times'] += 1
        try:
            dict_experiments[e['data']]['n_times'] += 1
            dict_experiments[e['data']]['exp_ids'].append(e['id'])
        except KeyError:
            dict_experiments[e['data']] = {'n_times': 1, 'exp_ids': [e['id']]}

    for i, (dataset, info) in enumerate(dict_experiments.items()):
        if i == 9:
            break
        experiments_df = experiments_df.append(
            {'dataset': dataset, 'times':info['n_times']}, ignore_index=True)

    if not os.path.exists('ubumlaas/static/tmp/'):
        os.mkdir('ubumlaas/static/tmp/')
    experiments_df.to_csv('ubumlaas/static/tmp/experiments.csv', index=False)
    exps_7d_df = exps_7d_df.sort_values(by='day', ascending=False)
    exps_7d_df.to_csv('ubumlaas/static/tmp/exp_7d.csv', index=False)

    cards_data = {
        "experiments": len(all_experiments),
        "users": len(users_info),
        "datasets": len(unique_datasets),
        "countries": len(unique.keys())
    }
    
    return render_template('admin/admin_dashboard.html', 
                           title="Dashboard", 
                           map=map._repr_html_(), 
                           cards_data=cards_data,
                           experiments=dict_experiments)

@admin.route("/administration/loading")
def processing():
    return render_template('admin/admin_loading.html')
