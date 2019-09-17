from flask import render_template, request, Blueprint

core = Blueprint('core', __name__)

@core.route('/')
def index():
    return render_template('index.html', title="UBUMLaaS")

@core.route('/info')
def info():
    return render_template('info.html', title="Información")

@core.route('/email')
def email():
    return render_template('email.html',title="Email Demo")
