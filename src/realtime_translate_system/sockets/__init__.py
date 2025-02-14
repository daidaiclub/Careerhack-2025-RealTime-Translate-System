from flask import Flask
from .audio_socket import init_socketio as audio_init_socketio
from .chat_socket import init_socketio as chat_init_socketio


def register_audio_sockets(app: Flask, recognizer, translation_service, term_matcher):
    socketio = app.container.socketio()
    socketio.init_app(app)
    audio_init_socketio(
        socketio, recognizer(), translation_service(), term_matcher()
    )

def register_chat_socket(app: Flask, meeting_processor):
    socketio = app.container.socketio()
    socketio.init_app(app)
    chat_init_socketio(socketio, meeting_processor())
