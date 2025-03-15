
from app.common.database import DBUser
from flask import Response, redirect

import config
import time
import jwt

def perform_login(
    user: DBUser,
    remember: bool = True,
    response: Response | None = None
) -> Response:
    response = response or redirect(f'/u/{user.id}')

    current_time = round(time.time())
    expiry = current_time + config.FRONTEND_TOKEN_EXPIRY
    expiry_refresh = current_time + config.FRONTEND_REFRESH_EXPIRY

    access_token = generate_token(user, expiry)
    refresh_token = generate_token(user, expiry_refresh)
    domain = f".{config.DOMAIN_NAME}" if not config.DEBUG else None

    response.set_cookie(
        'access_token',
        access_token,
        httponly=True,
        domain=domain,
        max_age=config.FRONTEND_TOKEN_EXPIRY
    )

    if remember:
        response.set_cookie(
            'refresh_token',
            refresh_token,
            httponly=True,
            domain=domain,
            max_age=config.FRONTEND_REFRESH_EXPIRY
        )

    return response

def perform_logout(response: Response | None = None) -> Response:
    response = response or redirect('/')
    response.delete_cookie('access_token')
    response.delete_cookie('refresh_token')
    return response

def generate_token(user: DBUser, expiry: int) -> str:
    return jwt.encode(
        {
            'id': user.id,
            'name': user.name,
            'exp': expiry,
        },
        config.FRONTEND_SECRET_KEY,
        algorithm='HS256'
    )

def validate_token(token: str) -> dict | None:
    try:
        data = jwt.decode(
            token,
            config.FRONTEND_SECRET_KEY,
            algorithms=['HS256']
        )
    except jwt.PyJWTError:
        return

    # Check if the token is expired
    if time.time() > data['exp']:
        return

    return data
