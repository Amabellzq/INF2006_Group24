# webapp/models/cart.py
from webapp.extensions import db
from datetime import datetime


class Cart(db.Model):
    __tablename__ = 'carts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Define the relationship back to User
    user = db.relationship('User', back_populates='cart')

    # Relationship to CartItem
    items = db.relationship('CartItem', backref='cart', cascade='all, delete')


class CartItem(db.Model):
    __tablename__ = 'cart_items'

    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('carts.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    quantity = db.Column(db.Integer, default=1, nullable=False)
    product_version = db.Column(db.Integer, nullable=False)

    product = db.relationship('Product', back_populates='cart_items')

    __table_args__ = (
        db.UniqueConstraint('cart_id', 'product_id', name='uq_cart_product'),
        db.CheckConstraint('quantity > 0', name='check_quantity_positive'),
    )