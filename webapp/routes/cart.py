# webapp/routes/cart.py
from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

cart_bp = Blueprint('cart', __name__)

@cart_bp.route('/cart')
@login_required  # Require the user to be logged in
def view_cart():
    # If the user is not logged in, @login_required will redirect them to the login page.

    # Add your cart retrieval logic here
    # Example: cart = Cart.query.filter_by(user_id=current_user.id).first()
    return render_template('cart.html')
