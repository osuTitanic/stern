
from app.common.database.repositories import users, verifications
from flask import Blueprint, request, abort, redirect
from datetime import datetime
from app.common import mail

import flask_login
import utils
import app

router = Blueprint('verification', __name__)

VerificationType = {
    'activation': 0,
    'password': 1
}

@router.get('/verification')
def verification():
    if not flask_login.current_user.is_anonymous:
        # User is logged in
        return redirect('/')

    try:
        verification_token = request.args.get('token', type=str)
        verification_id = request.args.get('id', type=int)
        type = request.args.get('type', 'activation')
    except ValueError:
        return abort(404)

    if type not in VerificationType.keys():
        return abort(404)

    if verification_id is None:
        return abort(404)

    with app.session.database.managed_session() as session:
        verification = verifications.fetch_by_id(
            verification_id,
            session=session
        )

        if not verification:
            return abort(404)

        if not verification_token:
            # Let user know, that they have received an email
            return utils.render_template(
                'verification.html',
                css='verification.css',
                verification=verification,
                title="Verification - osu!Titanic"
            )

        if verification_token != verification.token:
            return abort(404)

        if VerificationType[type] != verification.type:
            return abort(404)

        if type == 'activation':
            # Activate user
            verification.user.activated = True

            users.update(
                verification.user_id,
                {'activated': True},
                session=session
            )

        elif type == 'password':
            # Let user choose the password
            return utils.render_template(
                'verification.html',
                css='verification.css',
                verification=verification,
                title="Verification - osu!Titanic",
                reset=True
            )

        else:
            # How did they get here?
            return abort(404)

        verifications.delete(verification.token)

        utils.track(
            'website_verification_success',
            user=verification.user,
            properties={
                'verification_id': verification.id,
                'verification_type': verification.type
            }
        )

        app.session.logger.info(
            f'{verification.user.name} successfully verified their account.'
        )

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

    with app.session.database.managed_session() as session:
        try:
            if not (verification_id := request.args.get('id', type=int)):
                return abort(404)

            verification = verifications.fetch_by_id(
                verification_id,
                session=session
            )

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

        verifications.delete(
            verification.token,
            session=session
        )

        verification = verifications.create(
            verification.user_id,
            type=verification.type,
            token_size=32,
            session=session
        )

        mail.send_welcome_email(
            verification,
            verification.user
        )

        utils.track(
            'website_resend_verification',
            user=verification.user,
            properties={
                'verification_id': verification.id,
                'verification_type': verification.type
            }
        )

        app.session.logger.info(
            f'Resending verification email for {verification.user.name}...'
        )

        return redirect(f'/account/verification?id={verification.id}')
