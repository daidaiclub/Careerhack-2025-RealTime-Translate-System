from flask import Flask
from . import audio_socket


def register_sockets(app: Flask, recognizer, translation_service, term_matcher):
    socketio = app.container.socketio()
    socketio.init_app(app)
    audio_socket.init_socketio(
        socketio, recognizer(), translation_service(), term_matcher()
    )
