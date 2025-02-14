from dependency_injector import containers, providers
from realtime_translate_system.extensions import socketio
from realtime_translate_system.services import (
    AudioService,
    GoogleSpeechRecognizer,
    WhisperSpeechRecognizer,
    TranslationService,
    TermMatcher,
    TranscriptService,
    LLMService,
    EmbeddingService,
    MeetingProcessor,
    DatabaseService,
    TranslationService,
)


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()
    socketio = providers.Object(socketio)

    # LLM 服務
    llm_service_pro = providers.Factory(LLMService, model_name="gemini-1.5-pro-002")
    llm_service_flash = providers.Factory(LLMService, model_name="gemini-1.5-flash-002")

    # 基本服務
    recognizer = providers.Singleton(
        GoogleSpeechRecognizer, location=config.LOCATION, project_id=config.PROJECT_ID
    )

    term_matcher = providers.Singleton(
        TermMatcher,
        file_paths=config.FILE_PATHS,
        threshold=config.TERM_MATCHER_THRESHOLD,
    )

    translation_service = providers.Singleton(
        TranslationService, llm_service=llm_service_flash
    )

    transcript_service = providers.Singleton(
        TranscriptService,
        glossary_folder=config.FILE_PATHS,
        translation_service=translation_service,
        term_matcher=term_matcher,
    )

    embedding_service = providers.Singleton(
        EmbeddingService, model_name="text-multilingual-embedding-002"
    )

    database_service = providers.Singleton(
        DatabaseService, embedding_service=embedding_service
    )

    meeting_processor = providers.Singleton(
        MeetingProcessor,
        llm_service=llm_service_pro,
        db_service=database_service,
        embedding_service=embedding_service,
    )

    audio_service = providers.Factory(
        AudioService,
        upload_folder=config.UPLOAD_FOLDER,
        recognizer=recognizer,
        transcript_service=transcript_service,
        meeting_processor=meeting_processor,
    )
