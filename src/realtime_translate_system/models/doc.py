from datetime import datetime
from realtime_translate_system.models import db


class Doc(db.Model):  # 繼承 db.Model，定義 ORM 模型
    __tablename__ = "documents"  # 指定資料表名稱（可省略，預設會用類別名稱的小寫）

    id = db.Column(db.Integer, primary_key=True)  # 主鍵
    embedding = db.Column(db.Text, nullable=True)  # 向量嵌入（適合存 NumPy 陣列或列表）
    created_at = db.Column(
        db.DateTime, nullable=False, default=datetime.now
    )  # 建立時間
    updated_at = db.Column(
        db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now
    )  # 更新時間
    title = db.Column(db.Text, nullable=False)  # 標題
    keywords = db.Column(
        db.ARRAY(db.Text), nullable=True
    )  # 關鍵字（PostgreSQL 陣列類型）
    transcript_chinese = db.Column(db.Text, nullable=False, default="")
    transcript_english = db.Column(db.Text, nullable=False, default="")
    transcript_german = db.Column(db.Text, nullable=False, default="")
    transcript_japanese = db.Column(db.Text, nullable=False, default="")

    def __repr__(self):
        return f"<Document {self.title}, Last updated: {self.update_time}>"
