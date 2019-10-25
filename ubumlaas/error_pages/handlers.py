from flask import Blueprint, render_template

error_pages = Blueprint('error_pages', __name__)


@error_pages.app_errorhandler(404)
def error_404(error):
    """Render a 404 error.

    Arguments:
        error {Exception} -- exception which trigger handler

    Returns:
        str -- HTTP response with error page redered.
    """
    return render_template('error_pages/404.html'), 404


@error_pages.app_errorhandler(403)
def error_403(error):
    """Render a 403 error.

    Arguments:
        error {Exception} -- exception which trigger handler

    Returns:
        str -- HTTP response with error page redered.
    """
    return render_template('error_pages/403.html'), 403
