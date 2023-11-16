
from flask import Blueprint, request, redirect
import flask_login

router = Blueprint('logout', __name__)

@router.get('/logout')
def logout():
    redirect_url = request.args.get('redirect', '/')
    flask_login.logout_user()
    return redirect(redirect_url)
