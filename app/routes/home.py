
from __future__ import annotations

from app.common.database.repositories import plays, messages, posts, topics

from typing import Optional
from flask import (
    Blueprint,
    Response,
    redirect,
    request,
    Request
)

import utils
import app

router = Blueprint("home", __name__)

def handle_legacy_redirects(request: Request) -> Response | None:
    if not (page := request.args.get("p")):
        return

    if page == 'beatmap':
        if id := request.args.get("b"):
            return redirect(f'/b/{id}')
        elif id := request.args.get("s"):
            return redirect(f'/s/{id}')

    elif page == 'song':
        if id := request.args.get("s"):
            return redirect(f'/s/{id}')

    elif page == 'profile':
        if id := request.args.get("u"):
            return redirect(f'/u/{id}')

    elif page == 'download':
        return redirect('/download')

    elif page == 'team':
        return redirect('/g/1')

    elif page == 'beatmaplist':
        # TODO: Arguments
        return redirect('/beatmapsets')

    elif page == 'ranking':
        # TODO: Arguments
        return redirect('/rankings/osu/performance')

    elif page == 'countryranking':
        # TODO: Arguments
        return redirect('/rankings/osu/country')

    elif page == 'playerranking':
        # TODO: Arguments
        return redirect('/rankings/osu/performance')

def format_announcement(announcement: topics.DBForumTopic, session) -> dict:
    if (post := posts.fetch_initial_post(announcement.id, session=session)):
        text = post.content.splitlines()[0]

    return {
        "date": f"{announcement.created_at.day}.{announcement.created_at.month}.{announcement.created_at.year}",
        "link": f"/forum/{announcement.forum_id}/t/{announcement.id}",
        "title": announcement.title,
        "author": announcement.creator.name,
        "text": text if post else ""
    }

@router.get("/")
def root():
    if result := handle_legacy_redirects(request):
        return result

    with app.session.database.managed_session() as session:
        announcements = topics.fetch_announcements(4, 0, session=session)

        return utils.render_template(
            "home.html",
            css="home.css",
            title="Welcome - Titanic",
            description="Titanic » A private server for osu! that lets you experience the early days of the game.",
            news=[
                format_announcement(announcement, session=session)
                for announcement in announcements
            ],
            beatmapsets=[(p.count, p.beatmapset) for p in plays.fetch_most_played(session=session)],
            messages=messages.fetch_recent(session=session)
        )

# Redirect index.* to root
@router.get('/index')
@router.get('/index<extension>')
def index(extension: Optional[str] = None):
    return redirect('/')
