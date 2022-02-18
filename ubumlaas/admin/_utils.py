from flask import abort
from flask_login import current_user

def is_admin():
    if current_user.user_type != 0:
        abort(404)