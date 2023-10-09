
from flask import Blueprint, redirect

router = Blueprint('redirects', __name__)

# NOTE: These are just placeholders, until the
# beatmap pages will be getting implemented

@router.get('/s/<id>')
def beatmapset(id: int):
    return redirect(f'https://osu.ppy.sh/s/{id}')

@router.get('/b/<id>')
def beatmap(id: int):
    return redirect(f'https://osu.ppy.sh/b/{id}')
