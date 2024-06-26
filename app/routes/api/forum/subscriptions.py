
from app.models.forums import SubscriptionModel
from app.common.database import users

from flask import Blueprint, Response
from flask_login import current_user
from flask_pydantic import validate

import app

router = Blueprint("forum-subscriptions", __name__)

@router.get('/subscriptions')
@validate()
def get_subscriptions():
    if current_user.is_anonymous:
        return Response(
            response={},
            status=403,
            mimetype='application/json'
        )

    with app.session.database.managed_session() as session:
        subscriptions = users.fetch_subscriptions(
            current_user.id,
            session=session
        )

        subscriptions = [
            subscription
            for subscription in subscriptions
            if not subscription.topic.hidden
        ]

        return [
            SubscriptionModel.model_validate(subscription, from_attributes=True) \
                             .model_dump()
            for subscription in subscriptions
        ]
