
from app.common.database import beatmapsets, topics, posts, beatmaps
from app.common.webhooks import Embed, Author, Image
from app.common.database import DBUser, DBBeatmapset
from app.common.constants import DatabaseStatus
from app.common import officer

from flask_login import current_user, login_required
from flask import Blueprint, abort, redirect

import config
import app

router = Blueprint('beatmap-nuking', __name__)

def send_nuke_webhook(
    beatmapset: DBBeatmapset,
    user: DBUser
) -> None:
    embed = Embed(
        title=f'{beatmapset.artist} - {beatmapset.title}',
        url=f'http://osu.{config.DOMAIN_NAME}/s/{beatmapset.id}',
        thumbnail=Image(f'http://osu.{config.DOMAIN_NAME}/mt/{beatmapset.id}'),
        color=0xff0000
    )
    embed.author = Author(
        name=f'{user.name} nuked a Beatmap',
        url=f'http://osu.{config.DOMAIN_NAME}/u/{user.id}',
        icon_url=f'http://osu.{config.DOMAIN_NAME}/a/{user.id}'
    )
    officer.event(embeds=[embed])

@router.get('/<set_id>/nuke')
@login_required
def nuke_beatmap(set_id: int):
    if not current_user.is_bat:
        return abort(code=401)

    with app.session.database.managed_session() as session:
        if not (beatmapset := beatmapsets.fetch_one(set_id, session)):
            return redirect(f'/s/{set_id}')

        if not beatmapset.topic_id:
            return redirect(f'/s/{set_id}')

        if beatmapset.status > 0:
            return abort(code=400)

        if not (topic := topics.fetch_one(beatmapset.topic_id, session)):
            return redirect(f'/s/{set_id}')

        topics.update(
            topic.id,
            {
                'icon_id': 7,
                'forum_id': 12,
                'status_text': None,
                'hidden': True
            },
            session=session
        )

        posts.update_by_topic(
            topic.id,
            {
                'forum_id': 12,
                'hidden': True
            },
            session=session
        )

        beatmapsets.update(
            set_id,
            {'status': DatabaseStatus.Inactive.value},
            session=session
        )

        beatmaps.update_by_set_id(
            set_id,
            {'status': DatabaseStatus.Inactive.value},
            session=session
        )

        app.session.storage.remove_osz2(beatmapset.id)
        app.session.storage.remove_osz(beatmapset.id)
        app.session.storage.remove_background(beatmapset.id)
        app.session.storage.remove_mp3(beatmapset.id)

        for beatmap in beatmapset.beatmaps:
            app.session.storage.remove_beatmap_file(beatmap.id)

        send_nuke_webhook(
            beatmapset,
            current_user
        )

        app.session.logger.info(
            f'Beatmap "{beatmapset.full_name}" was nuked by {current_user.name}.'
        )

    return redirect(f'/s/{set_id}')
