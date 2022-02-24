from flask import abort
from flask_login import current_user
import variables as v
from ubumlaas.models import User
from geopy.geocoders import Nominatim
import numpy as np

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
    except:
        return np.nan
