from flask import render_template, Blueprint, send_from_directory, request, jsonify
from flask_login import login_required, current_user
from ubumlaas.models import User
from ._utils import is_admin
from sqlalchemy import text
import os
import variables as v

admin = Blueprint('admin', __name__)

@admin.route('/administration')
@login_required
def administration():
    is_admin()
    return render_template(
        'admin/administration.html', 
        user=current_user, 
        ip=request.environ.get('HTTP_X_REAL_IP', request.remote_addr),
        title="Administration")

@admin.route('/administration/users')
@login_required
def admin_users():
    is_admin()
    users_info = []
    for user in v.db.session.query(User).all():
        users_info.append(user.to_dict_all())

    return render_template('admin/admin_users.html', 
    ip=request.environ.get('HTTP_X_REAL_IP', request.remote_addr),
    user=current_user, 
    all_users=users_info,
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
            else:
                User.query.filter_by(id=id).update(
                    {'activated': 1}, synchronize_session=False)
                v.db.session.commit()
        except Exception:
            v.db.session.rollback()
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
            raise Exception('Can not make yourself no admin')
        option = request.args.get('option')

        try:
            if option == '1':
                User.query.filter_by(id=id).update(
                    {'user_type': 0}, synchronize_session=False)
                v.db.session.commit()
            else:
                User.query.filter_by(id=id).update(
                    {'user_type': 1}, synchronize_session=False)
                v.db.session.commit()
        except Exception:
            v.db.session.rollback()
            raise Exception('Failed to update DB')
        return 'ok'
    else:
        raise Exception('Failed to update DB')
