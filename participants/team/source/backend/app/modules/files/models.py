from app.extensions import db
from app.modules.shared.models import TimestampMixin

FILE_ACCESS_PUBLIC = "public"
FILE_ACCESS_PRIVATE = "private"
FILE_ACCESS_LEVELS = {FILE_ACCESS_PUBLIC, FILE_ACCESS_PRIVATE}


class FileAsset(TimestampMixin, db.Model):
    __tablename__ = "files"

    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    original_name = db.Column(db.String(255), nullable=False)
    stored_name = db.Column(db.String(255), unique=True, nullable=False, index=True)
    mime_type = db.Column(db.String(127), nullable=False)
    size_bytes = db.Column(db.Integer, nullable=False)
    access_scope = db.Column(db.String(32), default=FILE_ACCESS_PRIVATE, nullable=False, index=True)

    owner = db.relationship(
        "User",
        foreign_keys=[owner_id],
        backref=db.backref("uploaded_files", lazy="dynamic"),
    )

    def __repr__(self) -> str:
        return f"<FileAsset {self.id}:{self.original_name}>"

