
from app.common.database.repositories import users, verifications
from app.common import mail, officer, helpers
from app.common.constants import UserActivity
from app.common.helpers import activity
from app.accounts import perform_login

from flask import Blueprint, request, redirect
from flask_login import current_user
from datetime import datetime

import hashlib
import bcrypt
import utils
import app

router = Blueprint('login', __name__)

@router.get('/login')
def login_page():
    if not current_user.is_anonymous:
        # User has already logged in
        return redirect(f'/u/{current_user.id}')

    return render_login_page(redirect=request.args.get('redirect', None))

@router.post('/login')
def login():
    form = request.form.to_dict()
    username = form.get('username')
    password = form.get('password')
    redirect_url = form.get('redirect')
    remember = bool(form.get('remember'))

    ip = helpers.ip.resolve_ip_address_flask(request)
    login_attempts = app.session.redis.get(f'logins:{ip}') or 0

    if int(login_attempts) > 30:
        # Tell user to slow down
        officer.call(f'Too many login requests from ip! ({ip})')
        return render_login_page(
            error="Too many login attempts. Please wait a minute and try again!",
            redirect=redirect_url
        )

    app.session.redis.incr(f'logins:{ip}')
    app.session.redis.expire(f'logins:{ip}', time=30)

    with app.session.database.managed_session() as session:
        if not (user := users.fetch_by_name_extended(username, session=session)):
            return render_login_page(
                error="The specified username or password is incorrect.",
                redirect=redirect_url
            )

        md5_password = hashlib.md5(password.encode()).hexdigest()

        if not bcrypt.checkpw(md5_password.encode(), user.bcrypt.encode()):
            return render_login_page(
                error="The specified username or password is incorrect.",
                redirect=redirect_url
            )

        if not user.activated:
            # Get pending verifications
            pending_verifications = verifications.fetch_all_by_type(
                user.id,
                verification_type=0,
                session=session
            )

            pending_verifications.sort(
                key=lambda x: x.sent_at,
                reverse=True
            )

            if pending_verifications:
                verification = pending_verifications[0]

                # Check age of verification
                difference = (datetime.now() - verification.sent_at).seconds
                max_age = 60 * 60 * 12

                if difference > max_age:
                    # Delete old verification
                    verifications.delete(verification.token, session=session)

                    # Resend verification
                    verification = verifications.create(
                        user.id,
                        type=0,
                        token_size=32,
                        session=session
                    )

                    mail.send_welcome_email(verification, user)

            else:
                # No activation email was sent?
                verification = verifications.create(
                    user.id,
                    type=0,
                    token_size=32,
                    session=session
                )

                mail.send_welcome_email(verification, user)

            # Redirect to verification page
            return redirect(f'/account/verification?id={verification.id}')

        activity.submit(
            user.id, None,
            UserActivity.UserLogin,
            {
                'username': user.name,
                'location': 'website'
            },
            is_hidden=True,
            session=session
        )

        response = redirect(redirect_url or f'/u/{user.id}')
        response = perform_login(user, remember, response)
        return response

def render_login_page(
    error: str | None = None,
    redirect: str | None = None
) -> str:
    return utils.render_template(
        'login.html',
        css='account.css',
        error=error,
        redirect=redirect,
        disable_login_modal=True,
        title='Login - Titanic!',
        site_title='Login',
        site_description='Log in to your account and start playing today!'
    )
