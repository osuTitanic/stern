
from flask import Blueprint, request, redirect

import flask_login
import utils

router = Blueprint('logout', __name__)

@router.get('/logout')
def logout():
    if flask_login.current_user.is_anonymous:
        return redirect('/')

    redirect_url = request.args.get('redirect', '/')
    response = redirect(redirect_url)
    response.delete_cookie('access_token')
    response.delete_cookie('refresh_token')
    return response
