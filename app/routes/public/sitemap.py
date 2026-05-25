
from app.common.constants import BeatmapOrder, BeatmapSortBy, BeatmapCategory
from app.common.database import DBForum, DBForumTopic, DBWikiPage
from app.common.database.repositories import users, beatmapsets
from app.common.config import config_instance as config

from datetime import datetime, timedelta
from dataclasses import dataclass, field
from flask import Blueprint, Response
from xml.sax.saxutils import escape
from typing import List, Callable
from urllib.parse import quote

import app

@dataclass
class SitemapEntry:
    location: str
    priority: float
    change_frequency: str = 'daily'

@dataclass
class SitemapIndex:
    sitemaps: List['Sitemap']

    def render(self) -> str:
        for entry in self.sitemaps:
            entry.refresh()

        return (
            '<?xml version="1.0" encoding="UTF-8"?>' +
            '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' +
            ''.join(
                f'<sitemap>'
                f'<loc>{format_sitemap_path(entry.location)}</loc>'
                f'</sitemap>'
                for entry in self.sitemaps
            ) +
            '</sitemapindex>'
        )

@dataclass
class Sitemap:
    location: str
    generator: Callable
    entries: List[SitemapEntry] = field(default_factory=list)
    last_modified: datetime = datetime.now()
    refresh_interval: timedelta = timedelta(hours=1)

    def refresh(self) -> None:
        time_since_refresh = (
            datetime.now() - self.last_modified
        )

        if time_since_refresh < self.refresh_interval and self.entries:
            return

        self.entries = self.generator()
        self.last_modified = datetime.now()

    def render(self) -> str:
        self.refresh()

        return (
            '<?xml version="1.0" encoding="UTF-8"?>' +
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' +
            ''.join(
                f'<url>'
                f'<loc>{format_sitemap_path(entry.location)}</loc>'
                f'<priority>{entry.priority}</priority>'
                f'<changefreq>{entry.change_frequency}</changefreq>'
                f'</url>'
                for entry in self.entries
            ) +
            '</urlset>'
        )

def get_main_sites() -> List[SitemapEntry]:
    return [
        SitemapEntry('/', 1.0),
        SitemapEntry('/download/', 0.9),
        SitemapEntry('/beatmapsets/', 0.9),
        SitemapEntry('/beatmapsets/packs/', 0.8),
        SitemapEntry('/forum/', 0.9),
        SitemapEntry('/wiki/en/', 0.8),
        SitemapEntry('/events', 0.5),
        SitemapEntry('/rankings/osu/performance', 0.8),
        SitemapEntry('/rankings/osu/country', 0.7),
        SitemapEntry('/rankings/osu/rscore', 0.6),
        SitemapEntry('/rankings/osu/tscore', 0.5),
        SitemapEntry('/rankings/osu/ppv1', 0.4),
        SitemapEntry('/rankings/osu/clears', 0.4),
    ]

def get_top_users() -> List[SitemapEntry]:
    top_users = [
        user.id
        for user in users.fetch_recent(2000)
        if user.activated
    ]

    return [
        SitemapEntry(f'/u/{user_id}', 0.3, 'daily')
        for user_id in top_users
    ]

def get_most_played_beatmaps() -> List[SitemapEntry]:
    most_played_beatmaps = [
        canonical_id
        for beatmapset in beatmapsets.search_extended(
            None, None, None, None, None, None, None, None, None,
            sort=BeatmapSortBy.Plays,
            order=BeatmapOrder.Descending,
            category=BeatmapCategory.Leaderboard,
            has_storyboard=False,
            has_video=False,
            titanic_only=False,
            limit=1000
        )
        if (canonical_id := canonical_beatmap_id(beatmapset))
    ]

    return [
        SitemapEntry(f'/b/{beatmap_id}', 0.3, 'weekly')
        for beatmap_id in most_played_beatmaps
    ]

def get_recent_beatmaps() -> List[SitemapEntry]:
    recent_beatmaps = [
        canonical_id
        for beatmapset in beatmapsets.search_extended(
            None, None, None, None, None, None, None, None, None,
            sort=BeatmapSortBy.Created,
            order=BeatmapOrder.Descending,
            category=BeatmapCategory.Leaderboard,
            has_storyboard=False,
            has_video=False,
            titanic_only=False,
            limit=1000
        )
        if (canonical_id := canonical_beatmap_id(beatmapset))
    ]

    return [
        SitemapEntry(f'/b/{beatmap_id}', 0.3, 'daily')
        for beatmap_id in recent_beatmaps
    ]

def get_forums() -> List[SitemapEntry]:
    with app.session.database.managed_session() as session:
        site_forums = session.query(DBForum.id) \
            .filter(DBForum.hidden == False) \
            .filter(DBForum.parent_id.isnot(None)) \
            .order_by(DBForum.id.asc()) \
            .all()

    return [
        SitemapEntry(f'/forum/{forum_id}', 0.7, 'hourly')
        for forum_id, in site_forums
    ]

def get_forum_topics() -> List[SitemapEntry]:
    with app.session.database.managed_session() as session:
        site_topics = session.query(DBForumTopic.id, DBForumTopic.forum_id) \
            .join(DBForum, DBForum.id == DBForumTopic.forum_id) \
            .filter(DBForumTopic.hidden == False) \
            .filter(DBForum.hidden == False) \
            .order_by(DBForumTopic.last_post_at.desc()) \
            .limit(50000) \
            .all()

    return [
        SitemapEntry(f'/forum/{forum_id}/t/{topic_id}/', 0.5, 'daily')
        for topic_id, forum_id in site_topics
    ]

def get_wiki_pages() -> List[SitemapEntry]:
    with app.session.database.managed_session() as session:
        site_pages = session.query(DBWikiPage.path) \
            .order_by(DBWikiPage.path.asc()) \
            .all()

    return [
        SitemapEntry(f'/wiki/en/{path}', 0.6, 'weekly')
        for path, in site_pages
    ]

def canonical_beatmap_id(beatmapset) -> int | None:
    beatmaps = [
        beatmap
        for beatmap in beatmapset.beatmaps
        if beatmap.status > -3
    ]

    if not beatmaps:
        return None

    beatmaps.sort(key=lambda beatmap: (beatmap.mode, beatmap.diff))
    return beatmaps[0].id

router = Blueprint('sitemap', __name__)

def format_sitemap_path(location: str) -> str:
    encoded_location = quote(location, safe='/:?&=%#,+')
    return escape(f'{config.OSU_BASEURL.rstrip("/")}{encoded_location}')

def register_sitemap_url(entry: Sitemap) -> None:
    view_func = lambda entry=entry: Response(entry.render(), mimetype='application/xml')
    view_func.__name__ = f'sitemap_{entry.generator.__name__}'
    router.add_url_rule(
        entry.location,
        view_func=view_func
    )

popular_beatmaps_sitemap = Sitemap('/sitemap/beatmaps/popular.xml', get_most_played_beatmaps)
recent_beatmaps_sitemap = Sitemap('/sitemap/beatmaps/recent.xml', get_recent_beatmaps)
forum_sitemap = Sitemap('/sitemap/forum.xml', get_forums)
forum_topics_sitemap = Sitemap('/sitemap/forum/topics.xml', get_forum_topics)
user_sitemap = Sitemap('/sitemap/users.xml', get_top_users)
wiki_sitemap = Sitemap('/sitemap/wiki.xml', get_wiki_pages)
main_sitemap = Sitemap('/sitemap/main.xml', get_main_sites)
index_sitemap = SitemapIndex(
    [
        main_sitemap,
        user_sitemap,
        forum_sitemap,
        forum_topics_sitemap,
        wiki_sitemap,
        recent_beatmaps_sitemap,
        popular_beatmaps_sitemap
    ]
)

for entry in index_sitemap.sitemaps:
    register_sitemap_url(entry)

@router.get('/sitemap.xml')
def sitemap_xml():
    return Response(
        index_sitemap.render(),
        mimetype='application/xml'
    )
