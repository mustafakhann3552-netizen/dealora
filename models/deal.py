from datetime import datetime

from extensions import db


class Deal(db.Model):
    __tablename__ = "deals"

    # ==========================================
    # Primary Key
    # ==========================================

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # ==========================================
    # Basic Information
    # ==========================================

    title = db.Column(
        db.String(255),
        nullable=False
    )

    slug = db.Column(
        db.String(255),
        unique=True,
        nullable=False
    )

    short_description = db.Column(
        db.Text
    )

    meta_description = db.Column(
        db.Text
    )

    review = db.Column(
        db.Text
    )

    buying_guide = db.Column(
        db.Text
    )

    ai_generated = db.Column(
        db.Boolean,
        default=False
    )

    image = db.Column(
        db.String(255)
    )

    program_logo = db.Column(
        db.String(255)
    )

    affiliate_url = db.Column(
        db.Text
    )


    # ==========================================
    # Pricing
    # ==========================================

    old_price = db.Column(
        db.Float
    )

    new_price = db.Column(
        db.Float
    )

    discount = db.Column(
        db.Integer
    )

    # ==========================================
    # Product Card
    # ==========================================
    button_text = db.Column(
        db.String(50),
        default="View Deal"
    )

    badge = db.Column(
        db.String(100)
    )

    # ==========================================
    # Status
    # ==========================================

    featured = db.Column(
        db.Boolean,
        default=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    # ==========================================
    # Relationships
    # ==========================================

    store_id = db.Column(
        db.Integer,
        db.ForeignKey("stores.id"),
        nullable=False
    )

    category_id = db.Column(
        db.Integer,
        db.ForeignKey("categories.id"),
        nullable=False
    )

    store = db.relationship(
        "Store",
        backref="deals"
    )

    category = db.relationship(
        "Category",
        backref="deals"
    )

    # ==========================================
    # Object Representation
    # ==========================================

    def __repr__(self):
        return f"<Deal {self.id} - {self.title}>"