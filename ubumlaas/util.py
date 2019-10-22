import pandas as pd
import smtplib
import os
import numpy as np
import variables as v
import copy


def get_dataframe_from_file(path, filename):
    if filename.split(".")[-1] == "csv":
        file_df = pd.read_csv(path + filename)
    elif filename.split(".")[-1] == "xls":
        file_df = pd.read_excel(path + filename)
    else:
        raise Exception("Invalid format for "+filename)
    return file_df


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
    un = np.unique(y_test.values)
    d = {un[0]: True, un[1]: False}
    return pd.Series(y_test.values).map(d), pd.Series(y_pred).map(d)
