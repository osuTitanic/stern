
from flask import Blueprint

import time
import app

router = Blueprint("stats", __name__)

@router.route("/")
def server_stats():
    return {
        "uptime": round(time.time() - app.session.startup_time),
        "total_scores": int(app.session.redis.get("bancho:totalscores") or 0),
        "total_users": int(app.session.redis.get("bancho:totalusers") or 0),
        "online_users": int(app.session.redis.get("bancho:users") or 0)
    }
