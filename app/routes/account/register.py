
from app.common.constants.regexes import USERNAME, EMAIL
from app.common.database.repositories import users

from flask import Blueprint, request, redirect
from typing import Optional

import flask_login
import utils

router = Blueprint('register', __name__)

def validate_username(username: str) -> Optional[str]:
    if len(username) < 3:
        return "Your username is too short."

    if len(username) > 15:
        return "Your username is too long."

    if not USERNAME.match(username):
        return "Your username contains invalid characters."

    if users.fetch_by_safe_name(username.lower()):
        return "This username is already in use!"

def validate_email(email: str) -> Optional[str]:
    if not EMAIL.match(email):
        return "Please enter a valid email address!"

    if users.fetch_by_email(email.lower()):
        # TODO: Forgot username/password link
        return "This email address is already in use."

@router.get('/register')
def register():
    if not flask_login.current_user.is_anonymous:
        # User has already logged in
        return redirect(f'/u/{flask_login.current_user.id}')

    return utils.render_template(
        'register.html',
        css='register.css'
    )

@router.post('/register')
def registration_request():
    redirect_url = request.form.get('redirect', '/')
    ... # TODO
    return redirect(redirect_url)

@router.get('/register/check')
def input_validation():
    if not (type := request.args.get('type')):
        return

    if not (value := request.args.get('value')):
        return

    return {
        'username': validate_username,
        'email': validate_email
    }[type](value) or ''
