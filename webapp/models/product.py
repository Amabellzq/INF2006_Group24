from datetime import datetime
from webapp.extensions import db

from datetime import datetime
from webapp.extensions import db


class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    original_price = db.Column(db.Numeric(10, 2), nullable=False)
    discount_price = db.Column(db.Numeric(10, 2))

    # Store the raw image data here
    image_data = db.Column(db.LargeBinary(length=(2 ** 24 - 1)))
    stock = db.Column(db.Integer, default=0, nullable=False)
    is_flash_sale = db.Column(db.Boolean, default=False)
    flash_sale_start = db.Column(db.DateTime)
    flash_sale_end = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


    def __repr__(self):
        return f'<Product {self.name}>'
