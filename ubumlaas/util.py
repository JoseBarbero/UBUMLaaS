import pandas as pd
import smtplib
import os
import variables as v
import copy
import arff
import re
import numpy as np
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Message
from flask import url_for

def get_dataframe_from_file(path, filename, target_column=False):
    extension = filename.split(".")[-1]
    targets_indexes = None
    if extension == "csv":
        file_df = pd.read_csv(path + filename)
    elif extension == "xls":
        file_df = pd.read_excel(path + filename)
    elif extension == "arff":
        data = arff.load(open(path+filename, "r"), encode_nominal=True)
        columns = [row[0] for row in data["attributes"]]
        file_df = pd.DataFrame(data["data"], columns=columns)
        match = re.search(r'-C[ \t]+(-?\d)', data["relation"])
        if match:
            targets_indexes = match.group(1)
    else:
        raise Exception("Invalid format for "+filename)

    if target_column:
        return file_df, targets_indexes
    return file_df


def send_experiment_result_email(user, email, procid, result=None):
    """SEND an email with the result

    Arguments:
        user {str} -- username
        email {str} -- user's email
        procid {int} -- experiment identifier

    Keyword Arguments:
        result {str} -- Result of experiment (default: {None})
    """
    from ubumlaas.experiments.views.experiment import result_experiment

    subject = 'Your process on UBUMLaaS ' + str(procid) + ' has finished.'

    with v.app.app_context(), v.app.test_request_context():
        html = result_experiment(procid, admin= True)

        send_email(subject, email, html=html)


def send_email(subject, to=None, body=None, html=None):
    msg = Message(subject = subject, recipients = [to], body = body, html = html)
    v.mail.send(msg)


def generate_df_html(df, num=6):

    """Generates an html table from a dataframe.

    Arguments:
        df {dataframe} -- pandas dataframe with dataset

    Returns:
        str -- html dataframe
    """
    df.style.set_table_styles(
            [{'selector': 'tr:nth-of-type(odd)',
             'props': [('background', '#eee')]},
                {'selector': 'tr:nth-of-type(even)',
                    'props': [('background', 'white')]},
                {'selector': 'th',
                    'props': [('background', '#606060'),
                              ('color', 'white'),
                              ('font-family', 'verdana')]},
                {'selector': 'td',
                    'props': [('font-family', 'verdana')]}]
        ).hide_index()
    html_table = df.to_html(classes=["table", "table-borderless",
                                     "table-striped", "table-hover"],
                            col_space="100px", max_rows=num, justify="center")\
                   .replace("border=\"1\"", "border=\"0\"") \
                   .replace('<tr>',
                            '<tr align="center">')
    return html_table


def get_ensem_alg_name(conf, iteration=1):
    if "base_estimator" in conf["parameters"].keys():
        return v.app.jinja_env.filters["split"](conf["alg_name"]) \
            + "<br>"+("&nbsp;"*(4*iteration))+"⤿ "\
            + get_ensem_alg_name(
                conf["parameters"]["base_estimator"], iteration+1)
    else:
        return v.app.jinja_env.filters["split"](conf["alg_name"])


def get_dict_exp(name, dict_config):
    cd = copy.deepcopy(dict_config)
    d = {name: cd}
    if "base_estimator" in dict_config.keys():
        del d[name]["base_estimator"]
        d[name]["base_estimator"] = dict_config["base_estimator"]["alg_name"]
        name += dict_config["base_estimator"]["alg_name"]
        d.update(get_dict_exp(name,
                              dict_config["base_estimator"]["parameters"]))
        return d
    else:
        return d


def value_to_bool(y_test, y_pred):
    """Transform a pandas non boolean column in boolean column

    Arguments:
        y_test {pandas} -- test output
        y_pred {pandas} -- model output

    Returns:
        [pandas,pandas] -- test output boolean, model output boolean
    """
    un = y_test.unique()
    d = {un[0]: True, un[1]: False}
    return y_test.map(d), pd.Series(y_pred).map(d)


def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(v.app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=v.app.config['SECURITY_PASSWORD_SALT'])


def confirm_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(v.app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt=v.app.config['SECURITY_PASSWORD_SALT'],
            max_age=expiration
        )
    except:
        return False
    return email

def get_ngrok_url(endpoint, **values):
    return os.getenv("NGROK_URL")+url_for(endpoint, **values) if os.getenv("NGROK_URL") else url_for(endpoint, **values, _external=True)