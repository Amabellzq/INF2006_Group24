from flask import Blueprint, request, session, render_template, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from webapp.models import Order, Product
from webapp.extensions import db

order_bp = Blueprint('orders', __name__)


@order_bp.route('/orders')
@login_required
def order_list():
    """Display all orders placed by the current user."""
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template('order_list.html', orders=orders)


@order_bp.route('/orders/<int:order_id>')
@login_required
def order_detail(order_id):
    """Display order details for a specific order."""
    order = Order.query.get_or_404(order_id)

    # Ensure the user can only view their own orders
    if order.user_id != current_user.id:
        flash("Unauthorized access!", "danger")
        return redirect(url_for('orders.order_list'))

    product = Product.query.get(order.product_id)  # Fetch product details

    return render_template('order_detail.html', order=order, product=product)

# @order_bp.route("/toggle_voucher/<int:order_id>", methods=["POST"])
# @login_required
# def toggle_voucher(order_id):
#     order = Order.query.get(order_id)
#     if not order:
#         return jsonify({"success": False, "error": "Order not found"}), 404
#     new_status = request.json.get("voucher_status")
#     if new_status not in ["unused", "used"]:
#         return jsonify({"success": False, "error": "Invalid status"}), 400
#     order.voucher_status = new_status
#     db.session.commit()
    
#     return jsonify({"success": True, "voucher_status": order.voucher_status})

@order_bp.route("/toggle_voucher/<int:order_id>", methods=["POST"])
def toggle_voucher(order_id):
    order = Order.query.get(order_id)
    if not order:
        return jsonify({"success": False, "error": "Order not found"}), 404

    new_status = request.json.get("voucher_status")
    if new_status not in ["unused", "used"]:
        return jsonify({"success": False, "error": "Invalid status"}), 400

    order.voucher_status = new_status
    db.session.commit()

    return jsonify({"success": True, "voucher_status": order.voucher_status})