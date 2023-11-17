
from app.common.database.repositories import users
from flask import Blueprint, request, redirect

import flask_login
import hashlib
import bcrypt

router = Blueprint('login', __name__)

@router.post('/login')
def login():
    form = request.form.to_dict()
    username = form.get('username')
    password = form.get('password')
    redirect_url = form.get('redirect')
    remember = bool(form.get('remember'))

    if user := users.fetch_by_name(username):
        md5_password = hashlib.md5(password.encode()).hexdigest()

        if not bcrypt.checkpw(md5_password.encode(), user.bcrypt.encode()):
            return redirect(redirect_url or '/')

        if not user.activated:
            return redirect('/account/verification')

        flask_login.login_user(user, remember)
        return redirect(redirect_url or f'/u/{user.id}')

    return redirect(redirect_url or '/')
