from datetime import datetime
from realtime_translate_system.models import db


class Doc(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    transcript_chinese = db.Column(db.Text, nullable=False, default="")
    transcript_english = db.Column(db.Text, nullable=False, default="")
    transcript_german = db.Column(db.Text, nullable=False, default="")
    transcript_japanese = db.Column(db.Text, nullable=False, default="")
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    def __repr__(self):
        return f"<Doc {self.title}, {self.updated_at}>"
