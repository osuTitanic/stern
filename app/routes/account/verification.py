
from app.common.database.repositories import users, verifications
from flask import Blueprint, request, abort, redirect
from datetime import datetime
from app.common import mail

import flask_login
import bcrypt
import utils

router = Blueprint('verification', __name__)

@router.get('/verification')
def verification():
    if not flask_login.current_user.is_anonymous:
        # User is logged in
        return abort(404)

    try:
        verification_token = request.args.get('token', type=str)
        verification_id = request.args.get('id', type=int)
        type = request.args.get('type', 'activation')
    except ValueError:
        return abort(404)

    if type not in ('activation', 'password'):
        return abort(404)

    if verification_id is None:
        return abort(404)

    verification = verifications.fetch_by_id(verification_id)

    if not verification:
        return abort(404)

    if not verification_token:
        return utils.render_template(
            'verification.html',
            css='verification.css',
            verification=verification,
            title="Verification - osu!Titanic"
        )

    if verification_token != verification.token:
        return abort(404)

    if type == 'activation':
        verification.user.activated = True

        users.update(
            verification.user_id,
            {'activated': True}
        )

    else:
        # Let user choose the password
        return utils.render_template(
            'verification.html',
            css='verification.css',
            verification=verification,
            title="Verification - osu!Titanic"
        )

    verifications.delete(verification.token)

    return utils.render_template(
        'verification.html',
        css='verification.css',
        title="Verification - osu!Titanic",
        verification=verification,
        success=True
    )

@router.get('/verification/resend')
def resend_verification():
    if not flask_login.current_user.is_anonymous:
        # User is logged in
        return abort(404)

    try:
        if not (verification_id := request.args.get('id', type=int)):
            return abort(404)

        verification = verifications.fetch_by_id(verification_id)

        if not verification:
            return abort(404)

        difference = (datetime.now() - verification.sent_at).seconds

        if difference <= 120:
            # User has to wait two minutes
            return utils.render_template(
                'verification.html',
                css='verification.css',
                verification=verification,
                error='Please wait a few minutes, until you resend the email!',
                title="Verification - osu!Titanic"
            )
    except ValueError:
        return abort(404)

    verifications.delete(verification.token)

    verification = verifications.create(
        verification.user_id,
        type=verification.type,
        value=verification.value,
        token_size=32,
    )

    mail.send_welcome_email(verification, verification.user)

    return redirect(f'/account/verification?id={verification.id}')
