from dependency_injector import containers, providers
from realtime_translate_system.extensions import socketio
from realtime_translate_system.services import (
    AudioService,
    GoogleSpeechRecognizer,
    TranslationService,
    TermMatcher,
    LLMService, EmbeddingService,
    MeetingProcessor,
    DatabaseService
)
import vertexai

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
    
    vertexai.init(project=config.PROJECT_ID, location=config.LOCATION)

    llm_service = providers.Singleton(LLMService, model_name="gemini-1.5-pro-002")
    embedding_service = providers.Singleton(EmbeddingService, model_name="text-multilingual-embedding-002")
    
    database_service = providers.Singleton(
        DatabaseService,
        embedding_service=embedding_service
    )
    
    meeting_processor = providers.Singleton(
        MeetingProcessor,
        llm_service=llm_service,
        db_service=database_service,
        embedding_service=embedding_service
    )
