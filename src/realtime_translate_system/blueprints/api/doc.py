from flask import Blueprint, request, jsonify
from datetime import datetime
from realtime_translate_system.models import db
from realtime_translate_system.models.doc import Doc

doc_bp = Blueprint("doc", __name__)


@doc_bp.route("/", methods=["GET"])
def get_docs():
    docs = Doc.query.all()
    return jsonify(
        [
            {
                "id": doc.id,
                "title": doc.title,
                "content": doc.content,
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
                "content": doc.content,
                "updated_at": doc.updated_at.isoformat(),
            }
        )
    return jsonify({"error": "Doc not found"}), 404


@doc_bp.route("/", methods=["POST"])
def create_doc():
    data = request.get_json()
    title = data.get("title", "新會議")
    content = data.get("content", "")
    updated_at = datetime.now()

    new_doc = Doc(title=title, content=content, updated_at=updated_at)
    db.session.add(new_doc)
    db.session.commit()

    return jsonify({"id": new_doc.id})


@doc_bp.route("/", methods=["PUT"])
def update_doc():
    data = request.get_json()
    doc_id = data.get("id")
    title = data.get("title")
    content = data.get("content")
    updated_at = datetime.now()

    if not doc_id:
        return jsonify({"error": "Missing doc id"}), 400

    doc = Doc.query.get(doc_id)
    if not doc:
        return jsonify({"error": "Doc not found"}), 404

    doc.title = title
    doc.content = content
    doc.updated_at = updated_at
    db.session.commit()

    return jsonify({"status": "ok"})
