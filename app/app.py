
from app.common.database.repositories import users
from app.common.database.objects import DBUser

from flask import Flask, Request, redirect
from werkzeug.exceptions import NotFound
from flask_login import LoginManager
from typing import Tuple, Optional
from datetime import datetime

from . import common
from . import routes
from . import bbcode

import timeago
import config
import utils
import re

flask = Flask(
    __name__,
    static_url_path='',
    static_folder='static',
    template_folder='templates'
)

flask.register_blueprint(routes.router)
flask.secret_key = config.FRONTEND_SECRET_KEY

login_manager = LoginManager()
login_manager.init_app(flask)

@login_manager.user_loader
def user_loader(user_id: int) -> Optional[DBUser]:
    if user := users.fetch_by_id(user_id):
        return user

@login_manager.request_loader
def request_loader(request: Request):
    user_id = request.form.get('id')
    return user_loader(user_id)

@login_manager.unauthorized_handler
def unauthorized_user():
    return redirect('/?login=True')

@flask.template_filter('timeago')
def timeago_formatting(date: datetime):
    return timeago.format(date.replace(tzinfo=None), datetime.now())

@flask.template_filter('round')
def get_rounded(num: float, ndigits: int = 0):
    return round(num, ndigits)

@flask.template_filter('playstyle')
def get_rounded(num: int):
    return common.constants.Playstyle(num)

@flask.template_filter('domain')
def get_domain(url: str) -> str:
    return re.search(r'https?://([A-Za-z_0-9.-]+).*', url) \
             .group(1)

@flask.template_filter('twitter_handle')
def get_handle(url: str) -> str:
    url_match = re.search(r'https?://(www.)?(twitter|x)\.com/(@\w+|\w+)', url)

    if url_match:
        return url_match.group(3)

    if not url.startswith('@'):
        url = f'@{url}'

    return url

@flask.template_filter('short_mods')
def get_short(mods):
    return (
        common.constants.Mods(mods).short
        if mods else 'None'
    )

@flask.template_filter('get_level')
def get_user_level(total_score: int) -> int:
    next_level = common.constants.level.NEXT_LEVEL
    total_score = min(total_score, next_level[-1])

    for level, threshold in enumerate(next_level):
        if total_score < threshold:
            return level

    # Return the max level if total_score is higher than all levels
    return len(next_level)

@flask.template_filter('strftime')
def jinja2_strftime(date: datetime, format='%m/%d/%Y, %H:%M:%S'):
    native = date.replace(tzinfo=None)
    return native.strftime(format)

@flask.template_filter('format_activity')
def format_activity(activity_text: str, activity: common.database.DBActivity) -> str:
    links = activity.activity_links.split('||')
    args = activity.activity_args.split('||')
    items = tuple(zip(links, args))

    return activity_text \
        .format(
            *(
                f'<b><a href="{link}">{text}</a></b>'
                if '/u/' in link else
                f'<a href="{link}">{text}</a>'
                for link, text in items
            )
        )

@flask.template_filter('format_chat')
def format_chat(text: str) -> str:
    # Sanitize input text
    text = text.replace("<","&lt") \
               .replace(">", "&gt;")

    # Replace chat links with html links
    pattern = r'\[(.*?) (.*?)\]'
    replacement = r'<a href="\1">\2</a>'
    result = re.sub(pattern, replacement, text)

    # Remove action text
    result = result.replace('\x01ACTION', '') \
                   .replace('\x01', '')

    return result

@flask.template_filter('bbcode')
def render_bbcode(text: str) -> str:
    return f'<div class="bbcode">{bbcode.formatter.format(text)}</div>'

@flask.errorhandler(404)
def not_found(error: NotFound) -> Tuple[str, int]:
    return utils.render_template(
        content=error.description,
        name='404.html',
        css='404.css',
        title='Not Found - osu!Titanic'
    ), 404
