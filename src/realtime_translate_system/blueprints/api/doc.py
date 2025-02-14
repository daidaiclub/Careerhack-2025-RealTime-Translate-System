from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
from realtime_translate_system.models import db
from realtime_translate_system.models.doc import Doc

doc_bp = Blueprint("doc", __name__)


@doc_bp.route("/test", methods=["GET"])
def get_doeityocs():
    print("🔹 測試插入會議記錄...")
    current_app.container.database_service().insert_meeting(
        title="AI 發展趨勢",
        transcript_chinese="人工智能正在快速發展，對各行各業產生深遠影響。",
        transcript_english="Artificial intelligence is rapidly evolving and has a profound impact on various industries.",
        transcript_german="Künstliche Intelligenz entwickelt sich rasant und hat tiefgreifende Auswirkungen auf verschiedene Branchen.",
        transcript_japanese="人工知能は急速に進化しており、さまざまな業界に深い影響を与えています。",
        keywords=["AI", "Machine Learning", "科技"],
    )
    print("🔹 測試插入會議記錄完成")

    return jsonify({"status": "ok"})


@doc_bp.route("/", methods=["GET"])
def get_docs():
    docs = Doc.query.all()
    return jsonify(
        [
            {
                "id": doc.id,
                "title": doc.title,
                "transcript_chinese": doc.transcript_chinese,
                "transcript_english": doc.transcript_english,
                "transcript_german": doc.transcript_german,
                "transcript_japanese": doc.transcript_japanese,
                "updated_at": doc.updated_at.isoformat(),
            }
            for doc in docs
        ]
    )


@doc_bp.route("/<int:doc_id>", methods=["GET"])
def get_doc(doc_id):
    doc = Doc.query.get(doc_id)
    if doc:
        return jsonify(
            {
                "id": doc.id,
                "title": doc.title,
                "transcript_chinese": doc.transcript_chinese,
                "transcript_english": doc.transcript_english,
                "transcript_german": doc.transcript_german,
                "transcript_japanese": doc.transcript_japanese,
                "updated_at": doc.updated_at.isoformat(),
            }
        )
    return jsonify({"error": "Doc not found"}), 404


@doc_bp.route("/", methods=["POST"])
def create_doc():
    data = request.get_json()
    title = data.get("title", "新會議")
    transcript_chinese = data.get("transcript_chinese", "")
    transcript_english = data.get("transcript_english", "")
    transcript_german = data.get("transcript_german", "")
    transcript_japanese = data.get("transcript_japanese", "")
    updated_at = datetime.now()

    new_doc = Doc(
        title=title,
        transcript_chinese=transcript_chinese,
        transcript_english=transcript_english,
        transcript_german=transcript_german,
        transcript_japanese=transcript_japanese,
        updated_at=updated_at,
    )
    db.session.add(new_doc)
    db.session.commit()

    return jsonify({"id": new_doc.id})


@doc_bp.route("/", methods=["PUT"])
def update_doc():
    data = request.get_json()
    doc_id = data.get("id")
    title = data.get("title")
    transcript_chinese = data.get("transcript_chinese")
    transcript_english = data.get("transcript_english")
    transcript_german = data.get("transcript_german")
    transcript_japanese = data.get("transcript_japanese")
    updated_at = datetime.now()

    if not doc_id:
        return jsonify({"error": "Missing doc id"}), 400

    doc = Doc.query.get(doc_id)
    if not doc:
        return jsonify({"error": "Doc not found"}), 404

    doc.title = title
    doc.transcript_chinese = transcript_chinese
    doc.transcript_english = transcript_english
    doc.transcript_german = transcript_german
    doc.transcript_japanese = transcript_japanese
    doc.updated_at = updated_at
    db.session.commit()

    return jsonify({"status": "ok"})


@doc_bp.route("/<int:doc_id>", methods=["DELETE"])
def delete_doc(doc_id):
    doc = Doc.query.get(doc_id)
    if doc:
        db.session.delete(doc)
        db.session.commit()
        return jsonify({"status": "ok"})
    return jsonify({"error": "Doc not found"}), 404
