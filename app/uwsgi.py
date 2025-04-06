
from app.common.database import beatmapsets
from app import session

def on_startup() -> None:
    session.database.engine.dispose()
    session.database.wait_for_connection()
    session.redis.ping()

    # Run a test query
    beatmapsets.search("Nightcore", 0)

def setup_uwsgi() -> None:
    import uwsgi

    if uwsgi.opt.get("lazy_apps", False):
        return
    
    # If uwsgi is available, register the startup hook
    # and re-initialize the database and redis connections
    # to ensure they are available in the worker process.
    uwsgi.post_fork_hook = on_startup

try:
    setup_uwsgi()
except ImportError:
    pass
