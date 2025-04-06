
from __future__ import annotations

from app.common.constants import GameMode
from app.common.database import (
    beatmapsets,
    messages,
    topics,
    posts
)

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

@router.get("/")
def root() -> Response:
    if page := request.args.get("p"):
        return handle_legacy_redirects(page, request)

    with app.session.database.managed_session() as session:
        announcements = topics.fetch_announcements(4, 0, session=session)

        return utils.render_template(
            "home.html",
            css="home.css",
            title="Titanic! - Reviving old osu!",
            site_title="Titanic! - Reviving old osu!",
            site_description="Relive the early days of osu! with Titanic.",
            site_image=f"{app.config.OSU_BASEURL}/images/logo/main-low.png",
            site_url=app.config.OSU_BASEURL,
            news=[
                format_announcement(announcement, session=session)
                for announcement in announcements
            ],
            most_played=beatmapsets.fetch_most_played(session=session),
            messages=messages.fetch_recent(session=session)
        )

# Redirect index.* to root
@router.get('/index')
@router.get('/index<extension>')
def redirect_index(extension: Optional[str] = None) -> Response:
    if page := request.args.get("p"):
        return handle_legacy_redirects(page, request)

    return redirect(f'/?{request.query_string.decode()}')

@router.get('/p/<page>')
@router.get('/p/<page>/')
def redirect_page(page: str) -> Response:
    return handle_legacy_redirects(page, request)

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

def handle_legacy_redirects(page: str, request: Request) -> Response | None:
    if page == 'download':
        return redirect('/download')

    elif page == 'team':
        return redirect('/g/1')

    elif page == 'pp':
        return redirect('/rankings/osu/performance')

    elif page == 'ranking':
        return redirect('/rankings/osu/performance')

    elif page == 'countryranking':
        return redirect('/rankings/osu/country')

    elif page == 'player':
        if username := request.args.get("f"):
            return redirect(f'/u/{username}')

    elif page == 'profile':
        if id := request.args.get("u"):
            return redirect(f'/u/{id}')

    elif page == 'beatmap':
        if id := request.args.get("b"):
            return redirect(f'/b/{id}')

        elif id := request.args.get("s"):
            return redirect(f'/s/{id}')

    elif page == 'song':
        if id := request.args.get("b"):
            return redirect(f'/b/{id}')

        if id := request.args.get("s"):
            return redirect(f'/s/{id}')

    elif page == 'playerranking':
        mode = request.args.get("m", type=int)
        mode_string = "osu"

        if mode in (0, 1, 2, 3):
            mode_string = GameMode(mode).alias

        arguments = {
            'jumpto': request.args.get("f"),
            'country': request.args.get("c"),
            'page': request.args.get("page", type=int),
        }
        argument_string = "&".join(
            f"{key}={value}"
            for key, value in arguments.items()
            if value is not None
        )
        query_string = (
            "?" + argument_string
            if argument_string else ""
        )

        # Preserve the hash in the URL
        location = request.full_path.split("#")
        query_string += (
            "&" + location[-1]
            if len(location) > 1 and location[-1] else ""
        )

        return redirect(f'/rankings/{mode_string}/performance{query_string}')

    elif page == 'beatmaplist':
        arguments = {
            'language': request.args.get("la", type=int),
            'genre': request.args.get("g", type=int),
            'mode': request.args.get("m", type=int),
            'sort': request.args.get("s", type=int),
            'order': request.args.get("o", type=int),
            'query': request.args.get("q")
        }
        argument_string = "&".join(
            f"{key}={value}"
            for key, value in arguments.items()
            if value is not None
        )
        query_string = (
            "?" + argument_string
            if argument_string else ""
        )
        return redirect(f'/beatmapsets{query_string}')

    return redirect('/')
