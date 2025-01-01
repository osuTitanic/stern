
from app.common.database import users, logins, verifications
from app.common import mail

from flask_login import login_required, current_user
from flask import Blueprint, request, redirect

import flask_login
import hashlib
import bcrypt
import utils
import app

router = Blueprint('security-settings', __name__)

def get_security_page(
    error: str | None = None,
    info: str | None = None
) -> str:
    return utils.render_template(
        'settings/security.html',
        css='settings.css',
        error=error,
        info=info,
        logins=logins.fetch_many(
            flask_login.current_user.id,
            limit=5
        )
    )

@router.get('/security')
@login_required
def security_settings():
    return get_security_page()

@router.post('/security')
@login_required
def edit_account_details():
    with app.session.database.managed_session() as session:
        if not (current_password := request.form.get('current-password')):
            return get_security_page(error='Please enter your current password!')

        md5_password = hashlib.md5(current_password.encode()).hexdigest()

        if not bcrypt.checkpw(md5_password.encode(), current_user.bcrypt.encode()):
            return get_security_page(error='Your password was incorrect. Please try again!')

        new_email = request.form.get('new-email')
        email_confirm = request.form.get('email-confirm')

        if new_email and email_confirm:
            new_email = new_email.lower().strip()
            email_confirm = email_confirm.lower().strip()

            if new_email != email_confirm:
                return get_security_page(
                    error="The emails don't match. Please try again!"
                )

            if new_email == current_user.email:
                return get_security_page(
                    error="You're already using that email!"
                )

            if users.fetch_by_email(new_email, session=session):
                return get_security_page(
                    error="There already is a user with that email. Please choose another one, or reset your password!"
                )

            mail.send_email_changed(current_user)

            users.update(
                current_user.id,
                {
                    'activated': False,
                    'email': new_email
                },
                session=session
            )

            verification = verifications.create(
                current_user.id,
                type=0,
                session=session
            )
            current_user.email = new_email

            mail.send_reactivate_account_email(
                verification,
                current_user
            )

            flask_login.logout_user()
            return redirect(f'/account/verification?id={verification.id}')

        new_password = request.form.get('new-password')
        password_confirm = request.form.get('password-confirm')

        if new_password and password_confirm:
            if new_password != password_confirm:
                return get_security_page(error="The passwords don't match. Please try again!")

            hashed_password = bcrypt.hashpw(
                hashlib.md5(new_password.encode()) \
                    .hexdigest() \
                    .encode(),
                bcrypt.gensalt()
            ).decode()

            users.update(current_user.id, {'bcrypt': hashed_password}, session=session)
            mail.send_password_changed_email(current_user)

            return get_security_page(info='Your password was updated.')

        return redirect('/account/settings/profile')
