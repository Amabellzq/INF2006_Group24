from datetime import datetime
from webapp.extensions import db

class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=True)
    description = db.Column(db.Text,  nullable=True)
    original_price = db.Column(db.Numeric(10, 2), nullable=True)
    discount_price = db.Column(db.Numeric(10, 2), nullable=True)

    # ✅ Replace BLOB storage with an S3 URL (Max length set to 1024 to handle long URLs)
    image_url = db.Column(db.String(1024), nullable=True)

    stock = db.Column(db.Integer, default=0, nullable=True)
    is_flash_sale = db.Column(db.Boolean, default=True)
    flash_sale_start = db.Column(db.DateTime, nullable=True)
    flash_sale_end = db.Column(db.DateTime,  nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, )
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Product {self.name}>'
