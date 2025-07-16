
from flask import Blueprint, Response, abort, request
from typing import Optional

import utils
import app

# NOTE: These endpoints act as a fallback for
#       those provided in osuTitanic/deck.

router = Blueprint('avatar', __name__)

@router.get('/')
def default_avatar():
    if not (image := app.session.storage.get_avatar('unknown')):
        return abort(500, 'Failed to load default avatar')

    return Response(image, mimetype='image/png')

@router.get('/<filename>')
def avatar(filename: str):
    # Workaround for older clients that use filename extensions
    user_id = int(
        filename.replace('_000.png', '').replace('_000.jpg', '')
    )

    size = request.args.get(
        key='s',
        default=128,
        type=int
    )

    checksum = request.args.get(
        key='c',
        default=None,
        type=str
    )

    # If a checksum is provided, we can cache the avatar
    cache_header = (
        {'Cache-Control': 'public, max-age=86400'}
        if checksum is not None else {}
    )

    if (image := app.session.redis.get(f'avatar:{user_id}:{size}')):
        return Response(
            image,
            mimetype='image/png',
            headers=cache_header
        )

    if not (image := app.session.storage.get_avatar(user_id)):
        return default_avatar()

    allowed_sizes = (
        25,
        128,
        256
    )

    if size is not None and size in allowed_sizes:
        image = utils.resize_image(image, size)
        app.session.redis.set(f'avatar:{user_id}:{size}', image, ex=3600)

    return Response(
        image,
        mimetype='image/png',
        headers=cache_header
    )
