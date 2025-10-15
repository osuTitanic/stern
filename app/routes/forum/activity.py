
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
