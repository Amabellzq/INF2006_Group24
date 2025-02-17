# webapp/models/order.py
from webapp.extensions import db
from datetime import datetime

class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    unit_price = db.Column(db.Numeric(10, 2, asdecimal=False), nullable=False)
    total_amount = db.Column(db.Numeric(10, 2, asdecimal=False), nullable=False)
    status = db.Column(db.Enum('pending', 'paid', 'failed', 'refunded'), default='pending')
    voucher_status = db.Column(db.Enum('unused', 'used'), default='unused')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


    user = db.relationship('User', back_populates='orders')
    product = db.relationship('Product', backref='orders')  # Establishes Product.orders

    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'unit_price': float(self.unit_price),
            'total_amount': float(self.total_amount),
            'status': self.status,
            'voucher_status': self.voucher_status,
            'created_at': self.created_at.isoformat(),
            # Include product details if needed
            'product_name': self.product.name if self.product else None
        }