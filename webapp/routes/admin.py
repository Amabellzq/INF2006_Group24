# webapp/routes/admin.py
from flask import Blueprint, render_template, redirect, url_for
from flask import send_file, abort
from flask import request, flash
from flask_login import login_required, current_user
from webapp.extensions import db
from webapp.models.product import Product
from webapp.forms import ProductForm
from io import BytesIO


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

    if request.method == 'POST':
        try:
            if form.validate_on_submit():
                product = Product(
                    name=form.name.data,
                    description=form.description.data,
                    original_price=form.original_price.data,
                    discount_price=form.discount_price.data,
                    stock=form.stock.data
                )
                # Handle the image file
                image_file = request.files.get('image')
                if image_file and image_file.filename:
                    product.image_data = image_file.read()

                db.session.add(product)
                db.session.commit()

                flash('Product created successfully!', 'success')
                return redirect(url_for('admin.dashboard'))
            else:
                # Collect and flash individual errors
                error_messages = []
                for field, errors in form.errors.items():
                    for error in errors:
                        # e.g. "name: This field is required."
                        error_messages.append(f"{field}: {error}")

                if error_messages:
                    flash("Form validation failed. Errors: " + " | ".join(error_messages), 'error')
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred: {str(e)}", 'error')

    return render_template('admin_crud.html', form=form)


@admin_bp.route('/admin/products/<int:product_id>', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    """Edit an existing product (Admin Only)."""
    # Only admins can edit products
    if current_user.role != 'admin':
        flash("Unauthorized access!", "error")
        return redirect(url_for('main.home'))

    product = Product.query.get_or_404(product_id)
    form = ProductForm(obj=product)

    if form.validate_on_submit():
        try:
            form.populate_obj(product)  # Update non-image fields

            # Handle the image file upload
            image_file = request.files.get('image')
            if image_file and image_file.filename:
                product.image_data = image_file.read()  # Update image BLOB

            db.session.commit()
            flash("Product updated successfully!", "success")
            return redirect(url_for('admin.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred: {str(e)}", "error")

    if form.errors:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error in {field}: {error}", "error")

    return render_template('admin_crud.html', form=form, product=product)


@admin_bp.route('/admin/products/<int:product_id>/image')
@login_required
def product_image(product_id):
    """Serves the product image from the BLOB column."""
    if current_user.role != 'admin':
        return redirect(url_for('main.home'))

    product = Product.query.get_or_404(product_id)
    if not product.image_data:
        # If the product has no BLOB data, return a 404 or a placeholder
        abort(404, "No image for this product")

    # Return the image data as a file-like object
    return send_file(
        BytesIO(product.image_data),
        mimetype='image/jpeg',  # Or detect the actual image type if you store it
        as_attachment=False
    )


@admin_bp.route('/admin/products/<int:product_id>/delete', methods=['POST'])
@login_required
def delete_product(product_id):
    # Only admins can delete products
    if current_user.role != 'admin':
        return redirect(url_for('main.home'))

    product = Product.query.get_or_404(product_id)
    try:
        db.session.delete(product)
        db.session.commit()
        flash('Product deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting product: {str(e)}", 'error')

    return redirect(url_for('admin.dashboard'))

