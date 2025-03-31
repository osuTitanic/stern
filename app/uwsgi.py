
from app.common.database import beatmapsets
from app import session

def on_startup() -> None:
    session.database.engine.dispose()
    session.database.wait_for_connection()
    session.redis.ping()

    # Run a test query
    beatmapsets.search("Nightcore", 0)

try:
    import uwsgi

    # If uwsgi is available, register the startup hook
    # and re-initialize the database and redis connections
    # to ensure they are available in the worker process.
    uwsgi.post_fork_hook = on_startup
except ImportError:
    pass
