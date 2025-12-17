
import app

if __name__ == "__main__":
    app.common.profiling.setup()
    app.flask.run(
        host=app.session.config.FRONTEND_HOST,
        port=app.session.config.FRONTEND_PORT,
        debug=app.session.config.DEBUG
    )
