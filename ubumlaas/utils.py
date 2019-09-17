import smtplib

EMAIL_AC = 'ubumlaas@gmail.com'
EMAIL_PASS = 'rotationforest'


def send_email(user, email, procid, result=None):
    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()

        smtp.login(EMAIL_AC, EMAIL_PASS)

        subject = 'Your process on UBUMLaaS' + str(procid) + ' has finished.'

        body = 'Hi ' + user + ', your process ' + str(procid) + ', that were running on UBUMLaaS has finished.'
        if result is not None:
            body += "\nThe results is:\n"+result+"."

        msg = f'Subject: {subject}\n\n{body}'

        smtp.sendmail(EMAIL_AC, email, msg)