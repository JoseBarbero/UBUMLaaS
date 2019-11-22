import os
basedir = os.path.abspath(os.path.dirname(__file__))

SERVER_NAME = "localhost:5000"
SECRET_KEY = os.getenv("SECRET_KEY", "dev")
SECURITY_PASSWORD_SALT = os.getenv("SECURITY_PASSWORD_SALT", "password_salt")
TESTING = os.getenv("TESTING", "0") == "1"


# sqlalchemy configuration
SQLALCHEMY_DATABASE_URI = "sqlite:///"+os.path.join(basedir, "ubumlaas/data.sqlite")
SQLALCHEMY_TRACK_MODIFICATIONS = False


# flask-mail configuration
MAIL_SERVER = "smtp.gmail.com"
MAIL_PORT  = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_USERNAME = os.environ["EMAIL_AC"]
MAIL_PASSWORD = os.environ["EMAIL_PASS"]
MAIL_DEFAULT_SENDER = ("UBUMLaaS", MAIL_USERNAME) #tuple of name sender and mail sender
MAIL_DEBUG = False


