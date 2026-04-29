from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db
from app.modules.shared.models import TimestampMixin

user_roles = db.Table(
    "user_roles",
    db.Column(
        "user_id",
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    db.Column(
        "role_id",
        db.Integer,
        db.ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Role(TimestampMixin, db.Model):
    __tablename__ = "roles"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False, index=True)
    description = db.Column(db.String(255), nullable=True)

    def __repr__(self) -> str:
        return f"<Role {self.name}>"


class User(UserMixin, TimestampMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    display_name = db.Column(db.String(120), nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    active = db.Column(db.Boolean, default=True, nullable=False, index=True)
    avatar_file_id = db.Column(db.Integer, nullable=True, index=True)

    avatar_file = db.relationship(
        "FileAsset",
        primaryjoin="User.avatar_file_id == FileAsset.id",
        foreign_keys=[avatar_file_id],
        lazy="selectin",
        uselist=False,
    )

    roles = db.relationship(
        "Role",
        secondary=user_roles,
        lazy="selectin",
        backref=db.backref("users", lazy="dynamic"),
    )

    @property
    def is_active(self) -> bool:
        return self.active

    @property
    def is_admin(self) -> bool:
        return self.has_role("admin")

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def has_role(self, role_name: str) -> bool:
        return any(role.name == role_name for role in self.roles)

    def add_role(self, role: Role) -> None:
        if not self.has_role(role.name):
            self.roles.append(role)

    def remove_role(self, role_name: str) -> None:
        self.roles = [role for role in self.roles if role.name != role_name]

    def __repr__(self) -> str:
        return f"<User {self.email}>"
