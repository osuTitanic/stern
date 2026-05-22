
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from typing import Iterable
from flask import request

from app.common.database.repositories import topics
from app.common.database import DBForumTopic
from app.common.helpers import caching, ip
from app import accounts

import time
import app

FORUM_ACTIVITY_EXPIRY = 60*5

def mark_user_active(user_id: int, forum_id: int) -> None:
    redis_key = f"forum:{forum_id}:active:{user_id}"
    app.session.redis.set(redis_key, int(time.time()), ex=FORUM_ACTIVITY_EXPIRY)

def is_user_active(user_id: int, forum_id: int) -> bool:
    redis_key = f"forum:{forum_id}:active:{user_id}"
    last_active = app.session.redis.get(redis_key)

    if last_active is None:
        return False

    last_active = int(last_active)
    return (time.time() - last_active) < FORUM_ACTIVITY_EXPIRY

def get_active_users(forum_id: int) -> list[int]:
    pattern = f"forum:{forum_id}:active:*"
    keys = app.session.redis.keys(pattern)
    user_ids = [int(key.decode().split(":")[-1]) for key in keys]
    return user_ids

@caching.ttl_cache(ttl=60*5)
def fetch_average_topic_views() -> int:
    return int(topics.fetch_average_views())

def update_topic_read_state(topic_id: int) -> None:
    identifier = accounts.resolve_session_identifier()
    current_timestamp = datetime.now().timestamp()

    key = f'forums:topic_read_timestamps:{identifier}'
    app.session.redis.hset(key, topic_id, current_timestamp)
    app.session.redis.expire(key, 60 * 60 * 24 * 14)

def get_topic_read_timestamp(topic_id: int) -> float | None:
    identifier = accounts.resolve_session_identifier()
    key = f'forums:topic_read_timestamps:{identifier}'
    timestamp = app.session.redis.hget(key, topic_id)

    if timestamp is None:
        return None

    return float(timestamp)

def determine_read_status(topic: DBForumTopic) -> bool:
    if hasattr(topic, 'read_status'):
        # Use cached read status if available
        # This is a very hacky optimization, but I don't care
        return topic.read_status

    read_timestamp = get_topic_read_timestamp(topic.id)

    if read_timestamp is not None:
        return read_timestamp >= topic.last_post_at.timestamp()

    topic_age = datetime.now() - topic.created_at

    if topic_age >= timedelta(days=2):
        # Accounting for new accounts here that
        # haven't read any topics yet
        update_topic_read_state(topic.id)
        return True

    return False

def update_views(topic_id: int, session: Session) -> None:
    ip_address = ip.resolve_ip_address_flask(request)
    lock = app.session.redis.get(f'forums:viewlock:{topic_id}:{ip_address}')

    if lock:
        return

    topics.update(
        topic_id,
        {'views': DBForumTopic.views + 1},
        session=session
    )

    app.session.redis.set(
        f'forums:viewlock:{topic_id}:{ip_address}',
        value=1,
        ex=60
    )

def preload_topic_read_statuses(topic_list: Iterable[DBForumTopic]) -> None:
    topic_set = {topic.id: topic for topic in topic_list}
    topic_list = list(topic_set.values())

    if not topic_list:
        return

    identifier = accounts.resolve_session_identifier()
    key = f'forums:topic_read_timestamps:{identifier}'

    topic_ids = [topic.id for topic in topic_list]
    timestamps = app.session.redis.hmget(key, topic_ids)

    current_timestamp = datetime.now().timestamp()
    current_datetime = datetime.now()
    read_updates = {}

    for topic, timestamp in zip(topic_list, timestamps):
        if timestamp is not None:
            # If we have a timestamp, we can determine read status immediately
            topic.read_status = float(timestamp) >= topic.last_post_at.timestamp()
            continue

        # If no timestamp, we determine read status based on topic age
        topic_age = current_datetime - topic.created_at
        topic.read_status = topic_age >= timedelta(days=2)

        if topic.read_status:
            read_updates[topic.id] = current_timestamp

    if read_updates:
        # Apply any new read status updates
        app.session.redis.hset(key, mapping=read_updates)
        app.session.redis.expire(key, 60 * 60 * 24 * 14)
