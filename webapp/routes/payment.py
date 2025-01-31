from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from webapp.extensions import db
from webapp.models.product import Product
from webapp.models.order import Order
from webapp.forms import PaymentForm
from decimal import Decimal
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError

payment_bp = Blueprint('payment', __name__)


@payment_bp.route('/payment/<int:product_id>', methods=['GET', 'POST'])
@login_required
def payment_page(product_id):
    """Display payment page with form."""
    product = Product.query.get_or_404(product_id)
    price = product.discount_price or product.original_price
    form = PaymentForm()

    return render_template('payment.html', product=product, price=price, form=form)


from flask import request  # Ensure request is imported

@payment_bp.route('/process_payment/<int:product_id>', methods=['POST'])
@login_required
def process_payment(product_id):
    """Process payment and ensure ACID compliance."""
    product = Product.query.get_or_404(product_id)
    price = product.discount_price or product.original_price

    form = PaymentForm(request.form)  # Ensure form data is passed from POST request

    if form.validate_on_submit():
        try:
            with db.session.begin_nested():  # Maintain ACID properties
                new_order = Order(
                    user_id=current_user.id,
                    product_id=product.id,
                    unit_price=Decimal(str(price)),
                    total_amount=Decimal(str(price)),
                    status='paid',
                    created_at=datetime.utcnow()
                )
                db.session.add(new_order)

            db.session.commit()
            flash("Payment successful! Order created.", "success")
            return redirect(url_for('main.home'))

        except SQLAlchemyError as e:
            db.session.rollback()
            flash("An error occurred while processing the payment.", "error")
            return redirect(url_for('payment.payment_page', product_id=product_id))

    # 🔹 Capture Validation Errors
    errors = [f"{field}: {', '.join(error)}" for field, error in form.errors.items()]
    flash(f"Invalid payment details: {' | '.join(errors)}", "error")

    return redirect(url_for('payment.payment_page', product_id=product_id))


