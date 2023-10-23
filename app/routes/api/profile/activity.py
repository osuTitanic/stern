
from flask import Blueprint, abort
from typing import List

from app.common.database.repositories import activities
from app.common.constants import GameMode
from app.models import ActivityModel

router = Blueprint("activity", __name__)

@router.get('/<user_id>/activity/<mode>')
def recent_activity(
    user_id: int,
    mode: str
) -> List[dict]:
    if (mode := GameMode.from_alias(mode)) is None:
        return abort(400)

    recent_activity = [
        (
            activity,
            zip(
                activity.activity_links.split('||'),
                activity.activity_args.split('||')
            )
        )
        for activity in activities.fetch_recent(user_id, mode.value)
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
