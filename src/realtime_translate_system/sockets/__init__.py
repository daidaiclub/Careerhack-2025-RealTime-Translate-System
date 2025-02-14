from flask import Flask
from .audio_socket import init_socketio as audio_init_socketio
from .chat_socket import init_socketio as chat_init_socketio


def register_audio_sockets(app: Flask, recognizer, transcript_service, meeting_processor):
    socketio = app.container.socketio()
    socketio.init_app(app)
    audio_init_socketio(socketio, recognizer(), transcript_service(), meeting_processor())


def register_chat_socket(app: Flask, meeting_processor):
    socketio = app.container.socketio()
    chat_init_socketio(socketio, meeting_processor())
