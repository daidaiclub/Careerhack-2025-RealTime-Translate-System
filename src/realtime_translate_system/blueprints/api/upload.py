import os
from flask import Blueprint, request, jsonify, current_app as app
from werkzeug.utils import secure_filename

upload_bp = Blueprint("upload", __name__)


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]
    )


@upload_bp.route("/", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "沒有上傳文件"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "沒有選擇文件"}), 400
    
    print(file.filename)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)
        print(filepath)

        socketio = app.container.socketio()
        audio_service = app.container.audio_service()
        socketio.start_background_task(
            audio_service.process_audio, filename
        )

        return jsonify({"message": "文件上傳成功", "filename": filename})

    return jsonify({"error": "不允許的文件類型"}), 400
