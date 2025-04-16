
from app.models.forums import SubscriptionModel
from app.common.database import users, topics

from flask_login import current_user, login_required
from flask import Blueprint, request
from flask_pydantic import validate

import app

router = Blueprint("forum-subscriptions-api", __name__)

@router.get('/subscriptions')
@login_required
@validate()
def get_subscriptions():
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

@router.get('/subscriptions/add')
@login_required
@validate()
def add_subscription():
    return {
        'error': 501,
        'details': 'This endpoint is deprecated, please use the new API instead.'
    }

@router.get('/subscriptions/remove')
@login_required
@validate()
def remove_subscription():
    return {
        'error': 501,
        'details': 'This endpoint is deprecated, please use the new API instead.'
    }
