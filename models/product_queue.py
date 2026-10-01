from extensions import db
from datetime import datetime


class ProductQueue(db.Model):

    __tablename__ = "product_queue"

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(255), nullable=False)
    brand = db.Column(db.String(100))
    category = db.Column(db.String(100))

    price = db.Column(db.Float)
    old_price = db.Column(db.Float)
    discount = db.Column(db.Integer)

    description = db.Column(db.Text)

    image = db.Column(db.Text)
    affiliate_url = db.Column(db.Text)

    status = db.Column(db.String(20), default="pending")

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )