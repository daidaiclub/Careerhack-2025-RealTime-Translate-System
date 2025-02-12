from realtime_translate_system.blueprints.api import api_bp
from realtime_translate_system.blueprints.static_file import static_file_bp

def init_blueprints(app):
    app.register_blueprint(api_bp)
    app.register_blueprint(static_file_bp)