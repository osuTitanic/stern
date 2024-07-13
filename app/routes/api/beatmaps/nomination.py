
from app.common.database import beatmapsets, nominations, topics, posts
from app.common.webhooks import Embed, Author, Image
from app.common.database import DBUser, DBBeatmapset
from app.models.user import UserModel
from app.common import officer

from flask_login import current_user, login_required
from flask import Blueprint, abort, redirect

import config
import app

router = Blueprint('beatmap-nomination', __name__)

def send_nomination_webhook(
    beatmapset: DBBeatmapset,
    user: DBUser,
    type: str = 'add'
) -> None:
    author_text = {
        'add': f'{user.name} nominated a Beatmap',
        'reset': f'{user.name} reset all nominations',
    }
    color = {
        'add': 0x00da1d,
        'reset': 0xff0000,
    }
    embed = Embed(
        title=f'{beatmapset.artist} - {beatmapset.title}',
        url=f'http://osu.{config.DOMAIN_NAME}/s/{beatmapset.id}',
        thumbnail=Image(f'http://osu.{config.DOMAIN_NAME}/mt/{beatmapset.id}'),
        color=color.get(type)
    )
    embed.author = Author(
        name=author_text.get(type),
        url=f'http://osu.{config.DOMAIN_NAME}/u/{user.id}',
        icon_url=f'http://osu.{config.DOMAIN_NAME}/a/{user.id}'
    )
    officer.event(embeds=[embed])

def error_redirect(error: str, beatmapset: DBBeatmapset):
    return redirect(
        f'/b/{beatmapset.beatmaps[0].id}?bat_error={error}'
    )

@router.get('/nominations/<set_id>')
def get_nominations(set_id: int):
    with app.session.database.managed_session() as session:
        nominations_list = nominations.fetch_by_beatmapset(
            set_id,
            session=session
        )

        return [
            {
                'set_id': nom.set_id,
                'user_id': nom.user_id,
                'created_at': str(nom.time),
                'user': (
                    UserModel.model_validate(nom.user, from_attributes=True) \
                             .model_dump()
                )
            }
            for nom in nominations_list
        ]

@router.get('/nominations/<set_id>/add')
@login_required
def add_nomination(set_id: int):
    if not current_user.is_bat:
        return abort(code=401)

    with app.session.database.managed_session() as session:
        if not (beatmapset := beatmapsets.fetch_one(set_id, session)):
            return redirect(f'/s/{set_id}')

        if beatmapset.creator_id == current_user.id:
            # User is the creator of the beatmap
            return error_redirect(
                'You cannot nominate your own beatmap.',
                beatmapset
            )

        if nominations.fetch_one(set_id, current_user.id, session):
            # User already nominated that map
            return error_redirect(
                'You have already nominated this beatmap.',
                beatmapset
            )

        if beatmapset.status > 0:
            # Beatmap was already approved
            return error_redirect(
                'This beatmap was already ranked.',
                beatmapset
            )

        nominations.create(
            beatmapset.id,
            current_user.id,
            session=session
        )

        # Set icon to bubble
        topics.update(
            beatmapset.topic_id,
            {
                'icon_id': 3,
                'forum_id': 9,
                'status_text': 'Waiting for approval...'
            },
            session=session
        )

        posts.update_by_topic(
            beatmapset.topic_id,
            {'forum_id': 9},
            session=session
        )

        send_nomination_webhook(
            beatmapset,
            current_user,
            type='add'
        )

        app.session.logger.info(
            f'Beatmap "{beatmapset.full_name}" was nominated by {current_user.name}.'
        )

    return redirect(f'/s/{set_id}')

@router.get('/nominations/<set_id>/reset')
@login_required
def reset_nominations(set_id: int):
    if not current_user.is_bat:
        return abort(code=401)

    with app.session.database.managed_session() as session:
        if not (beatmapset := beatmapsets.fetch_one(set_id, session)):
            return redirect(f'/s/{set_id}')

        if beatmapset.status > 0:
            # Beatmap was already approved
            return error_redirect(
                'This beatmap was already ranked.',
                beatmapset
            )

        nominations.delete_all(
            beatmapset.id,
            session=session
        )

        # Set icon to popped bubble
        topics.update(
            beatmapset.topic_id,
            {
                'forum_id': 10,
                'icon_id': 4,
                'status_text': 'Waiting for further modding...'
            },
            session=session
        )

        posts.update_by_topic(
            beatmapset.topic_id,
            {'forum_id': 10},
            session=session
        )

        send_nomination_webhook(
            beatmapset,
            current_user,
            type='reset'
        )

        app.session.logger.info(
            f'{current_user.name} removed all nominations from "{beatmapset.full_name}".'
        )

    return redirect(f'/s/{set_id}')
