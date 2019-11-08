import pandas as pd
import smtplib
import os
import variables as v
import copy
import arff
import re
import numpy as np
from scipy.io.arff import loadarff

def get_dataframe_from_file(path, filename):
    extension = filename.split(".")[-1]
    if extension == "csv":
        file_df = pd.read_csv(path + filename)
        print(file_df.iloc[:,1].values.dtype)
    elif extension == "xls":
        file_df = pd.read_excel(path + filename)
    elif extension == "arff":
        data, meta =  loadarff(path+filename)
        
        file_df = pd.DataFrame(data, columns=meta.names())
        
    else:
        raise Exception("Invalid format for "+filename)
    return file_df

def get_targets_columns(path, filename):
    extension = filename.split(".")[-1]
    if extension == "arff":
        data =  arff.load(open(path+filename, "r"))
        match = re.search( r'-C[ \t]+(-?\d)', data["relation"])
        if match:
            return match.group(1)
    return None

def send_email(user, email, procid, result=None):
    """SEND an email with the result

    Arguments:
        user {str} -- username
        email {str} -- user's email
        procid {int} -- experiment identifier

    Keyword Arguments:
        result {str} -- Result of experiment (default: {None})
    """
    from ubumlaas.experiments.views.experiment import result_experiment

    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()

        smtp.login(os.environ["EMAIL_AC"], os.environ["EMAIL_PASS"])

        subject = 'Your process on UBUMLaaS ' + str(procid) + ' has finished.'

        with v.app.app_context(), v.app.test_request_context():
            body = result_experiment(procid, True)

        msg = f'Content-Type: text/html\nSubject: {subject}\n\n{body}'

        smtp.sendmail(os.environ["EMAIL_AC"], email, msg)


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


def get_ensem_alg_name(conf):
    if "base_estimator" in conf["parameters"].keys():
        return conf["alg_name"] + "-" + get_ensem_alg_name(
            conf["parameters"]["base_estimator"])
    else:
        return conf["alg_name"]


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
