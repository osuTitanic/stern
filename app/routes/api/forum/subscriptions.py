
from app.models.forums import SubscriptionModel
from app.common.database import users, topics

from flask_login import current_user, login_required
from flask import Blueprint, Response, request
from flask_pydantic import validate

import app

router = Blueprint("forum-subscriptions", __name__)

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
    if not (topic_id := request.args.get('topic_id', type=int)):
        return {
            'error': 400,
            'details': 'The request is missing the required "topic_id" parameter.'
        }, 400

    with app.session.database.managed_session() as session:
        if not (topic := topics.fetch_one(topic_id, session)):
            return {
                'error': 404,
                'details': 'The requested topic does not exist.'
            }, 404

        if topic.hidden:
            return {
                'error': 404,
                'details': 'The requested topic does not exist.'
            }, 404

        topics.add_subscriber(
            topic_id=topic.id,
            user_id=current_user.id,
            session=session
        )

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

@router.get('/subscriptions/remove')
@login_required
@validate()
def remove_subscription():
    if not (topic_id := request.args.get('topic_id', type=int)):
        return {
            'error': 400,
            'details': 'The request is missing the required "topic_id" parameter.'
        }, 400

    with app.session.database.managed_session() as session:
        topics.delete_subscriber(
            topic_id=topic_id,
            user_id=current_user.id,
            session=session
        )

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
