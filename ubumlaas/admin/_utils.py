import os
import time
import shutil
from flask import abort
from flask_login import current_user
import variables as v
from ubumlaas.models import User, Algorithm
from geopy.geocoders import Nominatim
import numpy as np
import pandas as pd
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
        except Exception as exc:
            v.app.logger.exception(exc)

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


def get_last_system_stats():
    byte_gib = 1 / 1073741824
    byte_mib = 1 / 1048576
    GiB = 'GiB'
    MiB = 'MiB'

    os.chdir(os.environ['LIBFOLDER'])
    glances_df = pd.read_csv(os.path.join('logs', 'monitor', 'glances.csv'))
    glances_dict = glances_df.iloc[-1].to_dict()

    mem_gib = glances_dict['mem_used'] * byte_gib
    if mem_gib > 1:
        glances_dict['mem_in_use'] = round(mem_gib, 2)
        glances_dict['mem_label'] = GiB
    else:
        glances_dict['mem_in_use'] = round(glances_dict['mem_used'] * byte_mib, 2)
        glances_dict['mem_label'] = MiB
    
    storage_used = glances_dict['fs_/_used'] * byte_gib
    if mem_gib > 1:
        glances_dict['storage_in_use'] = round(storage_used, 2)
        glances_dict['storage_label'] = GiB
    else:
        glances_dict['storage_in_use'] = round(
            glances_dict['fs_/_used'] * byte_mib, 2)
        glances_dict['storage_label'] = MiB
    
    max_storage = glances_dict['fs_/_size'] * byte_gib
    if mem_gib > 1:
        glances_dict['max_storage'] = round(max_storage, 2)
        glances_dict['max_storage_label'] = GiB
    else:
        glances_dict['max_storage'] = round(
            glances_dict['fs_/_size'] * byte_mib, 2)
        glances_dict['max_storage_label'] = MiB
    
    glances_dict['storage_in_use_percent'] = round(glances_dict['fs_/_used']/glances_dict['fs_/_size']*100, 1)

    time = glances_dict['uptime_seconds']
    day = time // (24 * 3600)
    time = time % (24 * 3600)
    hour = time // 3600
    time %= 3600
    minutes = time // 60
    time %= 60
    seconds = time
    glances_dict['uptime'] = "%d:%d:%d:%d" % (
        day, hour, minutes, seconds)

    return glances_dict
    
def get_system_load():
    os.chdir(os.environ['LIBFOLDER'])
    path = os.path.join('logs','monitor')
    data = {}

    try:
        current_df = pd.read_csv(path + "/glances.csv")
    except Exception:
        v.app.logger.exception('Logging file does not exist.')
        return None
    if current_df.shape[0] < 10:
        history_df = pd.read_csv(path + "/glances_history.csv")
        current_df = pd.concat([history_df, current_df], ignore_index=True)  

    system_load_10_df = current_df.tail(10)

    data['system_load_1'] = system_load_10_df['load_min1'].to_list()
    data['system_load_5'] = system_load_10_df['load_min5'].to_list()
    data['system_load_15'] = system_load_10_df['load_min15'].to_list()
    data['cpu_iowait'] = system_load_10_df['cpu_iowait'].to_list()
    data['diskio_sda_read_count'] = system_load_10_df['diskio_sda_read_count'].to_list()
    data['diskio_sda_write_count'] = system_load_10_df['diskio_sda_write_count'].to_list()
    data['network_enp4s0_rx'], data['network_enp4s0_rx_label'] = get_network_usage(
        system_load_10_df, 'network_enp4s0_rx')
    data['network_enp4s0_tx'], data['network_enp4s0_tx_label'] = get_network_usage(
        system_load_10_df, 'network_enp4s0_tx')
    data['timestamp'] = [x.split(' ')[1] for x in system_load_10_df['timestamp'].to_list()]

    return data

def get_network_usage(system_load_10_df, item):
    bitKiB = 1.220703e-4
    bitMiB = 1.192093e-7
    bitGiB = 1.16415332037e-10
    
    val = system_load_10_df[item].to_numpy()
    val_max = max(val)
    val_label = ''

    if val_max * bitGiB < 1:
        if val_max * bitMiB < 1:
            val = val * bitKiB
            val_label = 'KiB'
        else:
            val = val * bitMiB
            val_label = 'MiB'
    else:
        val = val * bitGiB
        val_label = 'GiB'
    
    return list(np.round(val, 2)), val_label
