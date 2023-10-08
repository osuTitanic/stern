
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
                "date": "13.04.23",
                "link": "/forum/p/2258963",
                "title": "The end of the MAT",
                "author": "Ephemeral",
                "text": "It has been a long road, and a hell of a journey. From the team's beginning as a measure to help address the slowing ranking cycle many years ago, the MAT have gone through a number of changes to become what they are today."
            },
            {
                "date": "13.04.15",
                "link": "/forum/p/2242727",
                "title": "osu! Public Release (b20130328)",
                "author": "DeathxShinigami",
                "text": "Hi everyone! DxS here as the new Chart Manager presenting the new April 2013 Chart."
            }
        ],
        beatmapsets=[(p.count, p.beatmapset) for p in plays.fetch_most_played()],
        messages=messages.fetch_recent(),
        featured_video_id="PYesuQugFOM"
    )
