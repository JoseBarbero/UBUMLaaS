from flask import render_template, Blueprint, send_from_directory
import os

core = Blueprint('core', __name__)


@core.route('/')
def index():
    """Renderize a index page.

    Returns:
        str -- HTTP response with rendered first page
    """
    return render_template('index-new.html', title="UBUMLaaS")


@core.route('/info')
def info():
    """Renderize a info page.

    Returns:
        str -- HTTP response with rendered info page
    """
    return render_template('info.html', title="Info")
