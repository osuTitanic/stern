
from app.common.database.repositories import users, verifications
from app.common import mail

from flask import Blueprint, request, redirect
from datetime import datetime

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
            # Get pending verifications
            pending_verifications = verifications.fetch_all_by_type(user.id, type=0)
            pending_verifications.sort(key=lambda x: x.sent_at, reverse=True)

            if pending_verifications:
                verification = pending_verifications[0]

                # Check age of verification
                difference = (datetime.now() - verification.sent_at).seconds
                max_age = 60 * 60 * 12

                if difference > max_age:
                    # Delete old verification
                    verifications.delete(verification.token)

                    # Resend verification
                    verification = verifications.create(
                        user.id,
                        type=0,
                        token_size=32
                    )

                    mail.send_welcome_email(verification, user)

            else:
                # No activation email was sent?
                verification = verifications.create(
                    user.id,
                    type=0,
                    token_size=32
                )

                mail.send_welcome_email(verification, user)

            # Redirect to verification page
            return redirect(f'/account/verification?id={verification.id}')

        flask_login.login_user(user, remember)
        return redirect(redirect_url or f'/u/{user.id}')

    return redirect(redirect_url or '/')
