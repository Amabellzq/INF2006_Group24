# webapp/models/order.py
from webapp.extensions import db
from datetime import datetime


class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    total_amount = db.Column(db.Numeric(10, 2, asdecimal=False), nullable=False)
    status = db.Column(db.Enum('pending', 'paid', 'failed', 'refunded'), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', back_populates='orders')

    items = db.relationship('OrderItem', backref='order', cascade='all, delete')

    def to_dict(self):
        return {
            'id': self.id,
            'total_amount': float(self.total_amount),
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'items': [item.to_dict() for item in self.items]
        }


class OrderItem(db.Model):
    __tablename__ = 'order_items'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(10, 2, asdecimal=False), nullable=False)

    def to_dict(self):
        return {
            'product_id': self.product_id,
            'quantity': self.quantity,
            'unit_price': float(self.unit_price)
        }