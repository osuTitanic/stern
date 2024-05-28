
from flask import Blueprint, redirect, request
from flask_login import login_required
from typing import Optional
from PIL import Image

import flask_login
import utils
import app
import io

router = Blueprint('avatar-settings', __name__)

def get_profile_page(error: Optional[str] = None):
    return utils.render_template(
        'settings/profile.html',
        css='settings.css',
        error=error
    )

@router.get('/avatar')
@login_required
def redirect_to_settings():
    return redirect('/account/settings/profile')

@router.post('/avatar')
@login_required
def update_avatar():
    if not (avatar := request.files.get('avatar')):
        return get_profile_page('Please provide a valid image!')

    if flask_login.current_user.restricted:
        return get_profile_page('Your account was restricted.')

    if flask_login.current_user.silence_end:
        return get_profile_page('Your account was silenced.')

    avatar.stream.seek(0, io.SEEK_END)
    size = avatar.stream.tell()

    if size > 1250**2: # Approx 1.5mb
        return get_profile_page('This image is too large. Please upload an image below 1.5mb!')

    try:
        image = Image.open(avatar)
    except Exception as e:
        app.session.logger.error(
            f'Failed to read image: {e}',
            exc_info=e
        )
        return get_profile_page('Please provide a valid image!')

    if (image.height > 5000) or (image.width > 5000):
        return get_profile_page('This image is too large. Please lower the resolution!')

    buffer = io.BytesIO()
    image.save(buffer, format='PNG')

    app.session.storage.upload_avatar(
        flask_login.current_user.id,
        buffer.getvalue()
    )

    app.session.logger.info(
        f'{flask_login.current_user.name} changed their avatar.'
    )

    return redirect('/account/settings/profile')
