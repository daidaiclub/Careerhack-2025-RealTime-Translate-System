from flask import Blueprint, send_from_directory
from werkzeug.exceptions import NotFound

static_file_bp = Blueprint("static_file", __name__)

@static_file_bp.route("/<path:filename>")
def static_files(filename):
    try:
        return send_from_directory("static", filename)
    except NotFound:
        return send_from_directory("static", "index.html")


@static_file_bp.route("/", defaults={"path": ""})
@static_file_bp.route("/<path:path>")
def catch_all(path: str):
    if path.startswith("api/"):
        return "API Not Found", 404
    return send_from_directory("static", "index.html")