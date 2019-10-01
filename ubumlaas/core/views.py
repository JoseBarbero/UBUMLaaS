from flask import render_template, request, Blueprint

core = Blueprint('core', __name__)

@core.route('/')
def index():
    """Renderize a index page.
    
    Returns:
        str -- HTTP response with rendered first page
    """
    return render_template('index.html', title="UBUMLaaS")

@core.route('/info')
def info():
    """Renderize a info page.
    
    Returns:
        str -- HTTP response with rendered info page
    """
    return render_template('info.html', title="Info")

