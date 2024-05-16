
from app.common.database.objects import DBUser, DBForum
from app.common.database.repositories import users
from app.common.helpers.external import location

from flask import Flask, Request, redirect
from werkzeug.exceptions import NotFound
from datetime import datetime, timedelta
from flask_login import LoginManager
from typing import Tuple, Optional

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
    if user := users.fetch_by_id(user_id, DBUser.groups, DBUser.relationships):
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

    index = 0
    score = 0

    while score + next_level[index] < total_score:
        score += next_level[index]
        index += 1

    return round((index + 1) + (total_score - score) / next_level[index])

@flask.template_filter('get_level_score')
def get_level_score(total_score: int) -> int:
    next_level = common.constants.level.NEXT_LEVEL
    total_score = min(total_score, next_level[-1])

    index = 0
    score = 0

    while score + next_level[index] < total_score:
        score += next_level[index]
        index += 1

    return total_score - score

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

@flask.template_filter('round_time')
def round_time(dt: datetime, round_to = 60):
    if dt == None : dt = datetime.now()
    seconds = (dt.replace(tzinfo=None) - dt.min).seconds
    rounding = (seconds+round_to/2) // round_to * round_to
    return dt + timedelta(0,rounding-seconds,-dt.microsecond)

@flask.template_filter('get_attributes')
def get_attributes(objects: list, name: str) -> list:
    return [getattr(o, name) for o in objects]

@flask.template_filter('clamp')
def clamp_value(value: int, minimum: int, maximum: int):
    return max(minimum, min(value, maximum))

@flask.template_filter('bbcode')
def render_bbcode(text: str) -> str:
    return f'<div class="bbcode">{bbcode.formatter.format(text)}</div>'

@flask.template_filter('bbcode_no_wrapper')
def render_bbcode_no_wrapper(text: str) -> str:
    return bbcode.formatter.format(text)

@flask.template_filter('bbcode_nowrap')
def render_bbcode_nowrapper(text: str) -> str:
    return bbcode.formatter.format(text)

@flask.template_filter('markdown_urls')
def format_markdown_urls(value: str) -> str:
    links = list(
        re.compile(r'\[([^\]]+)\]\(([^)]+)\)').findall(value)
    )

    for link in links:
        value = value.replace(
            f'[{link[0]}]({link[1]})',
            f'<a href="{link[1]}">{link[0]}</a>'
        )

    return value

@flask.template_filter('list_parent_forums')
def list_parent_forums(forum: DBForum) -> list:
    parent_forums = []

    while forum.parent_id:
        parent_forums.append(forum.parent)
        forum = forum.parent

    return parent_forums

@flask.template_filter('user_color')
def get_user_color(user: DBUser) -> str:
    if not user.groups:
        return "#000000"

    primary_group_id = min(get_attributes(user.groups, 'group_id'))
    primary_group = next(group for group in user.groups if group.group_id == primary_group_id).group
    return primary_group.color

@flask.errorhandler(404)
def not_found(error: NotFound) -> Tuple[str, int]:
    return utils.render_template(
        content=error.description,
        name='404.html',
        css='404.css',
        title='Not Found - osu!Titanic'
    ), 404
