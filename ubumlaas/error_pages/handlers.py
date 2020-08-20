from flask import Blueprint, render_template
import variables as v
from flask_login import current_user

error_pages = Blueprint('error_pages', __name__)


@error_pages.app_errorhandler(404)
def error_404(error):
    """Render a 404 error.

    Arguments:
        error {Exception} -- exception which trigger handler

    Returns:
        str -- HTTP response with error page redered.
    """
    uid = -1 if current_user.is_anonymous else current_user.id
    v.app.logger.warning("%d - Rendering 404 error", uid)
    return render_template('error_pages/404.html'), 404


@error_pages.app_errorhandler(403)
def error_403(error):
    """Render a 403 error.

    Arguments:
        error {Exception} -- exception which trigger handler

    Returns:
        str -- HTTP response with error page redered.
    """
    uid = -1 if current_user.is_anonymous else current_user.id
    v.app.logger.warning("%d - Rendering 403 error", uid)
    return render_template('error_pages/403.html'), 403
