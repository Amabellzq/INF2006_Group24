# webapp/routes/orders.py
from flask import Blueprint, request, session, render_template, redirect, url_for
from webapp.models import Order, OrderItem, Cart, CartItem, Product, order
from webapp.extensions import db

order_bp = Blueprint('orders', __name__)


@order_bp.route('/orders')
def order_list():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    orders = Order.query.filter_by(user_id=session['user_id']).order_by(Order.created_at.desc()).all()
    return render_template('order_list.html', orders=orders)


@order_bp.route('/orders/<int:order_id>')
def order_detail(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != session.get('user_id') and session.get('role') != 'admin':
        return redirect(url_for('home'))
    return render_template('order_detail.html', order=order)

