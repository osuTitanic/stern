
from app.common.database import forums, users, beatmapsets
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from flask import Blueprint
from typing import List

import app

@dataclass
class SitemapEntry:
    location: str
    priority: float
    change_frequency: str = 'daily'

@dataclass
class Sitemap:
    entries: List[SitemapEntry] = field(default_factory=list)
    last_modified: datetime = datetime.now()

    def refresh(self) -> None:
        time_since_refresh = (
            datetime.now() - self.last_modified
        )

        if time_since_refresh > timedelta(hours=1) and self.entries:
            return

        self.entries = generate_sitemap_entries()
        self.entries.sort(key=lambda entry: entry.priority, reverse=True)
        self.last_modified = datetime.now()

    def render(self) -> str:
        self.refresh()

        return (
            '<?xml version="1.0" encoding="UTF-8"?>' +
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' +
            ''.join(
                f'<url>'
                f'<loc>{entry.location}</loc>'
                f'<priority>{entry.priority}</priority>'
                f'<changefreq>{entry.change_frequency}</changefreq>'
                f'</url>'
                for entry in self.entries
            )
            + '</urlset>'
        )

def generate_sitemap_entries() -> List[SitemapEntry]:
    with app.session.database.managed_session() as session:
        top_users = [
            user.id
            for user in users.fetch_top(100, session)
        ]

        main_forums = [
            sub_forum.id
            for forum in forums.fetch_main_forums(session)
            for sub_forum in forums.fetch_sub_forums(forum.id, session)
        ]

        recent_beatmaps = [
            beatmapset.id
            for beatmapset in beatmapsets.search(
                'Newest', 1,
                session=session
            )
        ]

        most_played_beatmaps = [
            beatmapset.id
            for beatmapset in beatmapsets.search(
                'Most Played', 1,
                session=session
            )
        ]

    return [
        SitemapEntry('/', 1.0),
        SitemapEntry('/download/', 1.0),
        SitemapEntry('/beatmapsets/', 1.0),
        SitemapEntry('/forum/', 1.0),
        SitemapEntry('/rankings/osu/performance', 0.9),
        SitemapEntry('/rankings/osu/country', 0.7),
        SitemapEntry('/rankings/osu/rscore', 0.7),
        SitemapEntry('/rankings/osu/tscore', 0.7),
        SitemapEntry('/rankings/osu/ppv1', 0.7),
        SitemapEntry('/rankings/osu/clears', 0.7),
        *(
            SitemapEntry(f'/forum/{forum_id}', 0.7, 'hourly')
            for forum_id in main_forums
        ),
        *(
            SitemapEntry(f'/users/{user_id}', 0.5, 'hourly')
            for user_id in top_users
        ),
        *(
            SitemapEntry(f'/s/{beatmapset_id}', 0.5, 'hourly')
            for beatmapset_id in recent_beatmaps
        ),
        *(
            SitemapEntry(f'/s/{beatmapset_id}', 0.5, 'hourly')
            for beatmapset_id in most_played_beatmaps
        )
    ]

router = Blueprint('sitemap', __name__)
sitemap = Sitemap()

@router.get('/sitemap.xml')
def sitemap_xml():
    return sitemap.render()
