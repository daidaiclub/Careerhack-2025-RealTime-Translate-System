from dependency_injector import containers, providers
from realtime_translate_system.extensions import socketio
from realtime_translate_system.services import (
    AudioService,
    GoogleSpeechRecognizer,
    TranslationService,
    TermMatcher,
)


class Container(containers.DeclarativeContainer):
    """依賴注入容器，管理 Flask 內的服務"""

    config = providers.Configuration()
    socketio = providers.Object(socketio)

    recognizer = providers.Singleton(
        GoogleSpeechRecognizer, location=config.LOCATION, project_id=config.PROJECT_ID
    )
    translation_service = providers.Singleton(
        TranslationService, location=config.LOCATION, project_id=config.PROJECT_ID
    )
    term_matcher = providers.Singleton(
        TermMatcher,
        file_paths=config.FILE_PATHS,
        threshold=config.TERM_MATCHER_THRESHOLD,
    )

    audio_service = providers.Factory(
        AudioService,
        upload_folder=config.UPLOAD_FOLDER,
        recognizer=recognizer,
        translation_service=translation_service,
        term_matcher=term_matcher,
    )
