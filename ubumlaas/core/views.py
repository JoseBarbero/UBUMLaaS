from flask import render_template, Blueprint, send_from_directory, request
import os
import variables as v

core = Blueprint('core', __name__)


@core.route('/')
def index():
    """Renderize a index page.

    Returns:
        str -- HTTP response with rendered first page
    """
    v.app.logger.info("Rendering index-new page")
    return render_template('index.html', 
                           ip=request.environ.get(
                               'HTTP_X_REAL_IP', request.remote_addr),
                                title="UBUMLaaS")


@core.route('/info')
def info():
    """Renderize a info page.

    Returns:
        str -- HTTP response with rendered info page
    """
    v.app.logger.info("Rendering info page")
    return render_template('info.html', title="Info",
                           ip=request.environ.get(
                               'HTTP_X_REAL_IP', request.remote_addr))
