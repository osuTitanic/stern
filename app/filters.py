
from app.common.database import DBForumTopic, DBForum, DBUser
from app.common.helpers import activity
from datetime import datetime, timedelta
from urllib.parse import quote
from functools import cache
from .app import flask
from . import common
from . import bbcode
from . import git

import timeago
import utils
import math
import re

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

@flask.template_filter('playstyle')
def get_playstyle(num: int):
    return common.constants.Playstyle(num)

@flask.template_filter('url_quote')
def url_quote(url: str) -> str:
    return quote(url)

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
    text = text.replace("<","&lt") \
               .replace(">", "&gt;")

    # Replace chat links with html links
    pattern = r'\[([^\s\]]+)\s+(.+?)\]'
    replacement = r'<a href="\1">\2</a>'
    result = re.sub(pattern, replacement, text)

    # Remove action text
    result = result.replace('\x01ACTION', '') \
                   .replace('\x01', '')

    return result[:100] + f"{'...' if len(result) > 100 else ''}"

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
def get_user_color(user: DBUser, default='#4a4a4a') -> str:
    if not user.groups:
        return default

    primary_group_id = min(get_attributes(user.groups, 'group_id'))
    primary_group = next(group for group in user.groups if group.group_id == primary_group_id).group
    return primary_group.color

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
    if not (formatter := activity.formatters.get(entry.type)):
        return ""

    if not (result_text := formatter(entry, escape_brackets=True)):
        return ""

    return format_chat(result_text)
