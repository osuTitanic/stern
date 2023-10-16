
import signal
import config
import app

def on_exit(signal, frame):
    app.session.jobs.shutdown(
        cancel_futures=True,
        wait=False
    )
    exit()

signal.signal(signal.SIGINT, on_exit)

if __name__ == "__main__":
    app.session.jobs.submit(app.jobs.stats.update_usercount)
    app.session.jobs.submit(app.jobs.stats.update_stats)
    app.session.jobs.submit(app.jobs.stats.update_ranks)
    app.flask.run(
        host=config.FRONTEND_HOST,
        port=config.FRONTEND_PORT,
        debug=config.DEBUG
    )
