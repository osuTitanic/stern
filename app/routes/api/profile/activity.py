
from flask_pydantic import validate
from flask import Blueprint
from typing import List

from app.common.database.repositories import activities, users
from app.common.constants import GameMode
from app.models import ActivityModel

import app

router = Blueprint("activity", __name__)

@router.get('/<user_id>/activity/<mode>')
@validate()
def recent_activity(
    user_id: str,
    mode: str
) -> List[dict]:
    with app.session.database.managed_session() as session:
        if not user_id.isdigit():
            # Lookup user by username
            if not (user := users.fetch_by_name_extended(user_id, session=session)):
                return {
                    'error': 404,
                    'details': 'The requested user could not be found.'
                }, 404
            user_id = user.id

        if (mode := GameMode.from_alias(mode)) is None:
            return {
                'error': 400,
                'details': 'The requested mode does not exist.'
            }, 400

        recent_activity = [
            (
                activity,
                zip(
                    activity.activity_links.split('||'),
                    activity.activity_args.split('||')
                )
            )
            for activity in activities.fetch_recent(int(user_id), mode.value, session=session)
        ]

        return [
            ActivityModel(
                id=activity.id,
                user_id=activity.user_id,
                mode=activity.mode,
                time=activity.time,
                activity=activity.activity_text.format(
                    *(
                        f"[{text}]({link})"
                        for link, text in args
                    )
                )
            ).model_dump()
            for activity, args in recent_activity
        ]
