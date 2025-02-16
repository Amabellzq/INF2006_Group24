from datetime import datetime
from webapp.extensions import db

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, default="Unnamed Product")
    description = db.Column(db.Text, default="No description available.")  # ✅ Default text
    original_price = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    discount_price = db.Column(db.Numeric(10, 2), default=0.00)

    # ✅ Use default placeholder image if no S3 image is provided
    image_url = db.Column(db.String(1024), nullable=True, default="https://via.placeholder.com/400")

    stock = db.Column(db.Integer, default=0, nullable=False)
    is_flash_sale = db.Column(db.Boolean, default=False)
    flash_sale_start = db.Column(db.DateTime, default=None)  # ✅ Null by default
    flash_sale_end = db.Column(db.DateTime, default=None)  # ✅ Null by default
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Product {self.name}>'
