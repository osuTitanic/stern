
import signal
import config
import utils
import app

def on_exit(signal, frame):
    app.session.jobs.shutdown(
        cancel_futures=True,
        wait=False
    )
    exit()

signal.signal(signal.SIGINT, on_exit)

if __name__ == "__main__":
    app.flask.run(
        host=config.FRONTEND_HOST,
        port=config.FRONTEND_PORT,
        debug=config.DEBUG
    )
