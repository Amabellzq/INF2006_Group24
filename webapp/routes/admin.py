# webapp/routes/admin.py
from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from webapp.models.product import Product
from webapp.extensions import db
from webapp.forms import ProductForm

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin')
@login_required
def dashboard():
    # Check if the current user is actually an admin
    if current_user.role != 'admin':
        return redirect(url_for('main.home'))  # Adjust if your home endpoint is different

    products = Product.query.all()
    return render_template('admin_dashboard.html', products=products)

@admin_bp.route('/admin/products/new', methods=['GET', 'POST'])
@login_required
def create_product():
    # Only admins can create products
    if current_user.role != 'admin':
        return redirect(url_for('main.home'))

    form = ProductForm()
    if form.validate_on_submit():
        product = Product(
            name=form.name.data,
            description=form.description.data,
            original_price=form.original_price.data,
            discount_price=form.discount_price.data,
            stock=form.stock.data
        )
        db.session.add(product)
        db.session.commit()
        return redirect(url_for('admin.dashboard'))

    return render_template('admin_crud.html', form=form)

@admin_bp.route('/admin/products/<int:product_id>', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    # Only admins can edit products
    if current_user.role != 'admin':
        return redirect(url_for('main.home'))

    product = Product.query.get_or_404(product_id)
    form = ProductForm(obj=product)

    if form.validate_on_submit():
        form.populate_obj(product)
        db.session.commit()
        return redirect(url_for('admin.dashboard'))

    return render_template('admin_crud.html', form=form, product=product)
