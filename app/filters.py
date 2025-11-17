
from app.common.constants import OSU_CHAT_LINK_MODERN
from app.common.database import DBForumTopic, DBForum, DBUser
from app.common.helpers import activity
from app.common import bbcode

from datetime import datetime, timedelta
from urllib.parse import quote
from functools import cache

from .app import flask
from . import common
from . import git

import html
import flask_login
import timeago
import utils
import math
import re

REPLACE_ESCAPE = (
    ("&", "&amp;"),
    ("<", "&lt;"),
    (">", "&gt;"),
    ('"', "&quot;"),
    ("'", "&#39;"),
)

REPLACE_COSMETIC = (
    ("(c)", "&copy;"),
    ("(reg)", "&reg;"),
    ("(tm)", "&trade;"),
)

@flask.template_filter('any')
def any_filter(value: list) -> bool:
    return any(value)

@flask.template_filter('all')
def all_filter(value: list) -> bool:
    return all(value)

@flask.template_filter('timeago')
def timeago_formatting(date: datetime):
    return timeago.format(date.replace(tzinfo=None), datetime.now())

@flask.template_filter('round')
def get_rounded(num: float, ndigits: int = 0):
    return round(num, ndigits)

@flask.template_filter('floor')
def get_floored(num: float):
    return math.floor(num)

@flask.template_filter('url_quote')
def url_quote(url: str) -> str:
    return quote(url)

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
def get_level(total_score: int) -> int:
    if total_score <= 0:
        return 0

    next_level = common.constants.level.NEXT_LEVEL
    index = 0
    score = 0

    if total_score >= next_level[99]:
        return 100 + (total_score - next_level[99]) // 100000000000

    while score + next_level[index] < total_score:
        score += next_level[index]
        index += 1

    return (index + 1) + (total_score - score) / next_level[index]

@flask.template_filter('get_level_score')
def get_required_score_for_level(level: int) -> int:
    if level <= 0:
        return 0

    if level <= 100:
        return common.constants.level.NEXT_LEVEL[level - 1]

    return common.constants.level.NEXT_LEVEL[99] + 100000000000 * (level - 100)

@flask.template_filter('strftime')
def jinja2_strftime(date: datetime, format='%m/%d/%Y, %H:%M:%S'):
    native = date.replace(tzinfo=None)
    return native.strftime(format)

@flask.template_filter('format_chat')
def format_chat(text: str) -> str:
    # Sanitize input text
    for sequence, replace in REPLACE_ESCAPE:
        text = text.replace(sequence, replace)

    for sequence, replace in REPLACE_COSMETIC:
        text = text.replace(sequence, replace)

    # Replace chat links with html links
    replacement = r'<a href="\1">\2</a>'
    result = OSU_CHAT_LINK_MODERN.sub(replacement, text)

    # Remove /me text
    result = result.removeprefix('\x01ACTION') \
                   .removesuffix('\x01')

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
    return f'<div class="bbcode">{bbcode.render_html(text)}</div>'

@flask.template_filter('bbcode_no_wrapper')
def render_bbcode_no_wrapper(text: str) -> str:
    return bbcode.render_html(text)

@flask.template_filter('bbcode_nowrap')
def render_bbcode_nowrapper(text: str) -> str:
    return bbcode.render_html(text)

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
def get_user_color(user: DBUser) -> str | None:
    if not user.groups:
        return None

    groups = [ge.group for ge in user.groups if ge.group.color != '#000000']
    groups.sort(key=lambda g: g.id)

    if groups:
        return groups[0].color

@flask.template_filter('forum_user_link')
def get_forum_user_link(user: DBUser) -> str:
    color = get_user_color(user)

    if not color and flask_login.current_user.get_id() == user.id:
        # Highlight our own username
        color = '#310e7a'

    attributes = (
        f'class="username-colored" style="color: {color};"'
        if color else ''
    )

    return f'<a href="/u/{user.id}" {attributes}>{html.escape(user.name)}</a>'

@flask.template_filter('ceil')
def ceil(value: float) -> int:
    return math.ceil(value)

@flask.template_filter('required_nominations')
def get_required_nominations(beatmapset) -> int:
    return utils.required_nominations(beatmapset)

@flask.template_filter('git_asset_url')
@cache
def git_asset_url(url_path: str) -> str:
    commit = git.fetch_latest_commit_for_file('./app/static' + url_path)
    return f"{url_path}?commit={commit}" if commit else url_path

@flask.template_filter('get_status_icon')
def get_status_icon(topic: DBForumTopic) -> str:
    if topic.pinned or topic.announcement:
        if topic.locked_at:
            return "/images/icons/topics/announce_read_locked.gif"

        return "/images/icons/topics/announce_read.gif"

    if topic.locked_at:
        return "/images/icons/topics/topic_read_locked.gif"

    time = datetime.now() - topic.created_at
    views = utils.fetch_average_topic_views()

    if (topic.views > views) and (time.days < 7):
        return "/images/icons/topics/topic_read_hot.gif"

    # TODO: Read/Unread Logic
    return "/images/icons/topics/topic_read.gif"

@flask.template_filter('format_activity')
def format_activity(entry: common.database.DBActivity) -> str:
    if not (formatter := activity.web_formatters.get(entry.type)):
        return ""

    if not (result_text := formatter(entry)):
        return ""

    # Replace chat links with html links
    replacement = r'<a href="\1">\2</a>'
    return OSU_CHAT_LINK_MODERN.sub(replacement, result_text)

@flask.template_filter('avatar_url')
def avatar_url(user: DBUser, size: int | None = None) -> str:
    url_args = {}

    if size:
        url_args['s'] = f'{size}'

    if user.avatar_hash:
        url_args['c'] = user.avatar_hash

    if not url_args:
        return f'/a/{user.id}'

    url_args_string = "&".join(
        f"{k}={v}"
        for k, v in url_args.items()
    )

    return f'/a/{user.id}?{url_args_string}'

@flask.template_filter('format_number')
def format_number(number: int | float) -> str:
    return "{:,}".format(number)
