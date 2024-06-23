
from flask import Blueprint, request, redirect

import flask_login
import utils

router = Blueprint('logout', __name__)

@router.get('/logout')
def logout():
    if flask_login.current_user.is_anonymous:
        return redirect('/')

    utils.track(
        'website_logout',
        user=flask_login.current_user,
        properties={}
    )

    redirect_url = request.args.get('redirect', '/')
    flask_login.logout_user()
    return redirect(redirect_url)
