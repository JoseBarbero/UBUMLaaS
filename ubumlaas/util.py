import pandas as pd
import smtplib
import os
import variables as v


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
    from ubumlaas.experiments.views import result_experiment

    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()

        smtp.login(os.environ["EMAIL_AC"], os.environ["EMAIL_PASS"])

        subject = 'Your process on UBUMLaaS ' + str(procid) + ' has finished.'

        with v.app.app_context(), v.app.test_request_context():
            body = result_experiment(procid, True)

        #  body = 'Hi ' + user + ', your process ' + str(procid) + ', that were running on UBUMLaaS has finished.'
        """
        if result is not None:
        body += "\nThe results is:\n"+result+"."
        """

        msg = f'Content-Type: text/html\nSubject: {subject}\n\n{body}'

        smtp.sendmail(os.environ["EMAIL_AC"], email, msg)

