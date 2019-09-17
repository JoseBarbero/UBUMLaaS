from flask import render_template, request, Blueprint
import variables as v
import time
from ubumlaas.jobs import WorkerBuilder

core = Blueprint('core', __name__)

@core.route('/')
def index():
    return render_template('index.html', title="UBUMLaaS")

@core.route('/info')
def info():
    return render_template('info.html', title="Information")


