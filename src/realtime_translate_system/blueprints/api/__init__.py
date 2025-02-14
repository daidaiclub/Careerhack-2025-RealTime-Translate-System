from flask import Blueprint
from realtime_translate_system.blueprints.api.doc import doc_bp
from realtime_translate_system.blueprints.api.upload import upload_bp

api_bp = Blueprint("api", __name__, url_prefix="/api")

api_bp.register_blueprint(doc_bp, url_prefix="/doc")
api_bp.register_blueprint(upload_bp, url_prefix="/upload")