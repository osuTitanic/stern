
from flask import Blueprint, request, redirect
from app import accounts

import flask_login
import utils

router = Blueprint('logout', __name__)

@router.post('/logout')
def logout():
    if flask_login.current_user.is_anonymous:
        return redirect('/')

    redirect_url = request.form.get('redirect', '/')
    return accounts.perform_logout(redirect(redirect_url))
