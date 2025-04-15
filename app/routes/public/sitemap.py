
from app.common.constants import BeatmapOrder, BeatmapSortBy, BeatmapCategory
from app.common.database import forums, users, beatmapsets

from datetime import datetime, timedelta
from dataclasses import dataclass, field
from flask import Blueprint, Response
from typing import List, Callable

import config
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
                f'<loc>{config.OSU_BASEURL}{entry.location}</loc>'
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

        if time_since_refresh > self.refresh_interval and self.entries:
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
                f'<loc>{config.OSU_BASEURL}{entry.location}</loc>'
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
        SitemapEntry('/forum/', 0.9),
        SitemapEntry('/account/register', 0.8),
        SitemapEntry('/account/login', 0.8),
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

def get_forums() -> List[SitemapEntry]:
    with app.session.database.managed_session() as session:
        site_forums = [forum.id for forum in forums.fetch_all(session)]
        site_forums.sort()

    return [
        SitemapEntry(f'/forum/{forum_id}', 0.7, 'hourly')
        for forum_id in site_forums
    ]

def get_most_played_beatmaps() -> List[SitemapEntry]:
    most_played_beatmaps = [
        beatmapset.id
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
    ]

    return [
        SitemapEntry(f'/s/{beatmapset_id}', 0.3, 'weekly')
        for beatmapset_id in most_played_beatmaps
    ]

def get_recent_beatmaps() -> List[SitemapEntry]:
    recent_beatmaps = [
        beatmapset.id
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
    ]

    return [
        SitemapEntry(f'/s/{beatmapset_id}', 0.3, 'daily')
        for beatmapset_id in recent_beatmaps
    ]

router = Blueprint('sitemap', __name__)

popular_beatmaps_sitemap = Sitemap('/sitemap/beatmaps/popular.xml', get_most_played_beatmaps)
recent_beatmaps_sitemap = Sitemap('/sitemap/beatmaps/recent.xml', get_recent_beatmaps)
forum_sitemap = Sitemap('/sitemap/forum.xml', get_forums)
user_sitemap = Sitemap('/sitemap/users.xml', get_top_users)
main_sitemap = Sitemap('/sitemap/main.xml', get_main_sites)
index_sitemap = SitemapIndex(
    [
        main_sitemap,
        user_sitemap,
        forum_sitemap,
        recent_beatmaps_sitemap,
        popular_beatmaps_sitemap
    ]
)

if config.DOMAIN_NAME in ('titanic.sh', 'localhost'):
    for entry in index_sitemap.sitemaps:
        view_func = lambda entry=entry: Response(entry.render(), mimetype='application/xml')
        view_func.__name__ = f'sitemap_{entry.generator.__name__}'

        router.add_url_rule(
            entry.location,
            view_func=view_func
        )

    @router.get('/sitemap.xml')
    def sitemap_xml():
        return Response(
            index_sitemap.render(),
            mimetype='application/xml'
        )
