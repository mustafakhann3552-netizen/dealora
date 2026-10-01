from datetime import datetime

from extensions import db


class Blog(db.Model):
    __tablename__ = "blogs"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    title = db.Column(
        db.String(255),
        nullable=False
    )

    slug = db.Column(
        db.String(255),
        unique=True,
        nullable=False
    )

    image = db.Column(
        db.String(255)
    )

    short_description = db.Column(
        db.Text
    )

    content = db.Column(
        db.Text
    )

    featured = db.Column(
        db.Boolean,
        default=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    def __repr__(self):
        return f"<Blog {self.title}>"