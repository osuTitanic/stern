
import config
import app

if __name__ == "__main__":
    app.common.profiling.setup()
    app.flask.run(
        host=config.FRONTEND_HOST,
        port=config.FRONTEND_PORT,
        debug=config.DEBUG
    )
