
from app.common.database.repositories import plays, messages

from flask import Blueprint, render_template, redirect
from typing import Optional

from . import stats

router = Blueprint("routes", __name__)
router.register_blueprint(stats.router, url_prefix='/stats')

@router.get('/index')
@router.get('/index<extension>')
def index(extension: Optional[str] = None):
    return redirect('/')

@router.get("/")
def root():
    return render_template(
        "home.html",
        css="home.css",
        news=[
            {
                "date": "08.10.2023",
                "link": "#",
                "title": "Welcome!",
                "author": "Lekuru",
                "text": "This website is currently in development, so enjoy this placeholder message!"
            }
        ],
        beatmapsets=[(p.count, p.beatmapset) for p in plays.fetch_most_played()],
        messages=messages.fetch_recent(),
        featured_video_id="PYesuQugFOM"
    )
