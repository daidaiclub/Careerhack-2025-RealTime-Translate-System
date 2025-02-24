from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
from realtime_translate_system.models import db
from realtime_translate_system.models.doc import Doc

doc_bp = Blueprint("doc", __name__)


@doc_bp.route("/test", methods=["GET"])
def get_doeityocs():
    print("🔹 測試插入會議記錄...")
    current_app.container.database_service().insert_document(
        title="區塊鏈與金融科技",
        transcript_chinese="區塊鏈技術已被廣泛應用於金融科技領域。",
        transcript_english="Blockchain technology has been widely applied in the fintech industry.",
        transcript_german="Blockchain-Technologie wird in der Fintech-Branche weit verbreitet eingesetzt.",
        transcript_japanese="ブロックチェーン技術はフィンテック業界で広く活用されています。",
        keywords=["Blockchain", "Fintech", "金融科技"],
    )
    print("🔹 測試插入會議記錄完成")

    return jsonify({"status": "ok"})


@doc_bp.route("/", methods=["GET"])
def get_docs():
    docs = current_app.container.database_service().get_documents()
    return jsonify([doc.to_dict() for doc in docs])


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

    _, keywords = current_app.container.document_service().gen_title_keywords(
        transcript_chinese
    )

    if not doc_id:
        return jsonify({"error": "Missing doc id"}), 400

    doc = Doc.query.get(doc_id)
    if not doc:
        return jsonify({"error": "Doc not found"}), 404

    current_app.container.database_service().update_document(
        doc_id=doc_id,
        title=title,
        transcript_chinese=transcript_chinese,
        transcript_english=transcript_english,
        transcript_german=transcript_german,
        transcript_japanese=transcript_japanese,
        keywords=keywords,
    )

    return jsonify({"status": "ok"})


@doc_bp.route("/<int:doc_id>", methods=["DELETE"])
def delete_doc(doc_id):
    doc = Doc.query.get(doc_id)
    if doc:
        db.session.delete(doc)
        db.session.commit()
        return jsonify({"status": "ok"})
    return jsonify({"error": "Doc not found"}), 404
