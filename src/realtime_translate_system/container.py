from dependency_injector import containers, providers
from realtime_translate_system.extensions import socketio
from realtime_translate_system.repository.doc_repository import DocRepository
from realtime_translate_system.services.audio import AudioService
from realtime_translate_system.services.speech import (
    GoogleSpeech2TextService,
    WhisperSpeech2TextService,
)
from realtime_translate_system.services.llm import VertexLLMService
from realtime_translate_system.services.embedding import VertexEmbeddingService
from realtime_translate_system.services.translation import TranslationService
from realtime_translate_system.services.document import RAGService


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()
    socketio = providers.Object(socketio)

    # LLM 服務
    llm_service_pro = providers.Factory(VertexLLMService, model_name="gemini-1.5-pro-002")
    llm_service_flash = providers.Factory(VertexLLMService, model_name="gemini-1.5-flash-002")

    # 基本服務
    recognizer = providers.Singleton(
        WhisperSpeech2TextService, model_size="turbo"
    )

    # term_matcher = providers.Singleton(
    #     TermMatcher,
    #     file_paths=config.FILE_PATHS,
    #     threshold=config.TERM_MATCHER_THRESHOLD,
    # )

    translation_service = providers.Singleton(
        TranslationService, llm_service=llm_service_flash
    )

    embedding_service = providers.Singleton(
        VertexEmbeddingService, model_name="text-multilingual-embedding-002"
    )

    doc_repostiory = providers.Singleton(
        DocRepository, embedding_service=embedding_service
    )

    document_service = providers.Singleton(
        RAGService,
        llm_service=llm_service_pro,
        db_service=doc_repostiory,
        embedding_service=embedding_service,
    )

    audio_service = providers.Factory(
        AudioService,
        upload_folder=config.UPLOAD_FOLDER,
        recognizer=recognizer,
        translation_service=translation_service,
        document_service=document_service,
    )
