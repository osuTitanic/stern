
from app.common.database.repositories import users
from flask_login import login_required, current_user
from flask import Blueprint, redirect, request
from datetime import datetime
from typing import Optional
from PIL import Image

import hashlib
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

    if current_user.restricted:
        return get_profile_page('Your account was restricted.')

    if current_user.silence_end and \
       current_user.silence_end > datetime.now():
        return get_profile_page('Your account was silenced.')

    if not current_user.activated:
        return get_profile_page('Your account is not activated.')

    avatar.stream.seek(0, io.SEEK_END)
    size = avatar.stream.tell()

    if size > 2.5 * 1024 * 1024:
        return get_profile_page('This image is too large. Please upload an image below 2.5mb!')

    try:
        image = Image.open(avatar)
    except Exception as e:
        app.session.logger.error(
            f'Failed to read image: {e}',
            exc_info=e
        )
        return get_profile_page('Please provide a valid image!')

    if (image.height > 1000) or (image.width > 1000):
        return get_profile_page('This image is too large. Please lower the resolution!')

    buffer = io.BytesIO()
    image = image.resize((256, 256))
    image.save(buffer, format='PNG')

    app.session.storage.upload_avatar(
        current_user.id,
        buffer.getvalue()
    )
    
    users.update(
        current_user.id,
        {
            'avatar_hash': hashlib.md5(buffer.getvalue()).hexdigest(),
            'avatar_last_update': datetime.now()
        }
    )

    # Remove avatar checksum cache, if it exists
    app.session.redis.delete(
        f'bancho:avatar_hash:{current_user.id}'
    )

    app.session.logger.info(
        f'{current_user.name} changed their avatar.'
    )

    return redirect('/account/settings/profile')
