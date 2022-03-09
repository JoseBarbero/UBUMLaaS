import time
import shutil
from flask import abort
from flask_login import current_user
import variables as v
from ubumlaas.models import User, Algorithm
from geopy.geocoders import Nominatim
import numpy as np
from datetime import datetime


def is_admin():
    if current_user.user_type != 0:
        abort(404)


def get_users_info():
    is_admin()
    users_info = []
    for user in v.db.session.query(User).all():
        users_info.append(user.to_dict_all())
    return users_info


def geolocate(country):
    geolocator = Nominatim(user_agent="http")
    try:
        loc = geolocator.geocode(country)
        return (loc.latitude, loc.longitude)
    except Exception:
        return np.nan


def exps_type(exps):
    types = {}
    type_time = {}
    algorithms = {}
    for a in Algorithm.query.all():
        a = a.to_dict()
        algorithms[a['alg_name']] = a['alg_typ']
        types[a['alg_typ']] = 0
        type_time[a['alg_typ']] = 0

    for e in exps:
        e = e.to_dict()
        types[algorithms[e['alg']['alg_name']]] += 1
        try:
            end_time = datetime.fromtimestamp(e['endtime'])
            start_time = datetime.fromtimestamp(e['starttime'])
            diff_time = end_time - start_time
            type_time[
                algorithms[e['alg']['alg_name']]] += diff_time.total_seconds()
        except Exception:
            v.app.logger.exception()

    return types, type_time


def clear_tmp_csvs(path):
    time.sleep(5)
    try:
        shutil.rmtree(path)
        v.app.logger.info(
            "Directory '%s' has been removed successfully" % path)
    except Exception:
        v.app.logger.info(
            "Directory '%s' could not be deleted" % path)
