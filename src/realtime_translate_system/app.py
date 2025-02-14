"""Flask application entry point with Socket.IO support."""

import os
from flask import Flask
from flask_cors import CORS
import vertexai
from realtime_translate_system.blueprints import init_blueprints
from realtime_translate_system.config import config
from realtime_translate_system.container import Container
from realtime_translate_system.extensions import socketio
from realtime_translate_system.models import db
from realtime_translate_system.sockets import register_audio_sockets, register_chat_socket


def create_app() -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__, static_folder="static")
    CORS(app)  # Allow cross-origin requests

    env = os.environ.get("FLASK_ENV", "development")
    app.config.from_object(config[env])

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    container = Container()
    container.config.from_dict(app.config)
    app.container = container

    vertexai.init(project=container.config.PROJECT_ID(), location=container.config.LOCATION())

    db.init_app(app)
    with app.app_context():
        db.create_all()
    init_blueprints(app)
    register_audio_sockets(
        app, container.recognizer, container.translation_service, container.term_matcher
    )
    register_chat_socket(app, container.meeting_processor)


    return app


if __name__ == "__main__":
    APP = create_app()
    socketio.run(APP, debug=True, host="0.0.0.0", port=5000)