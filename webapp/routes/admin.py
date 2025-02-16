# webapp/routes/admin.py
from flask import Blueprint, render_template, redirect, url_for
from flask import send_file, abort
from flask import request, flash
from flask_login import login_required, current_user
from webapp.extensions import db
from webapp.models.product import Product
from webapp.forms import ProductForm
from io import BytesIO
from sqlalchemy import or_  # ✅ Add this line

from webapp.utils.s3_helper import upload_file_to_s3
from webapp.utils.utils import admin_required
from botocore.exceptions import NoCredentialsError, ClientError  # ✅ Import AWS error handling


admin_bp = Blueprint('admin', __name__)

# @admin_bp.route('/admin')
# @login_required
# def dashboard():
#     # Check if the current user is actually an admin
#     if current_user.role != 'admin':
#         return redirect(url_for('main.home'))  # Adjust if your home endpoint is different

#     products = Product.query.all()
#     return render_template('admin_dashboard.html', products=products)

@admin_bp.route('/admin')
@admin_required
def dashboard():
    search_query = request.args.get('search', '').strip()

    if search_query:
        products = Product.query.filter(
            or_(
                Product.name.ilike(f"%{search_query}%"),
                Product.description.ilike(f"%{search_query}%")
            )
        ).all()
    else:
        products = Product.query.all()

    return render_template('admin_dashboard.html', products=products, search_query=search_query)




@admin_bp.route('/admin/products/new', methods=['GET', 'POST'])
@admin_required
def create_product():
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

                # ✅ Handle the image file
                image_file = request.files.get('image')
                if image_file and image_file.filename:
                    try:
                        product.image_url = upload_file_to_s3(image_file)  # ✅ Upload & store S3 URL
                    except NoCredentialsError:
                        flash("❌ AWS Credentials not found. Ensure Flask is running with the correct IAM role.",
                              "error")
                        return redirect(url_for('admin.create_product'))
                    except ClientError as e:
                        error_code = e.response['Error']['Code']
                        flash(f"❌ S3 Upload Failed: {error_code} - {str(e)}", "error")
                        return redirect(url_for('admin.create_product'))
                    except Exception as e:
                        flash(f"❌ Unexpected error during S3 upload: {str(e)}", "error")
                        return redirect(url_for('admin.create_product'))

                db.session.add(product)
                db.session.commit()

                flash('✅ Product created successfully!', 'success')
                return redirect(url_for('admin.dashboard'))
            else:
                # Collect and flash individual errors
                error_messages = []
                for field, errors in form.errors.items():
                    for error in errors:
                        error_messages.append(f"{field}: {error}")

                if error_messages:
                    flash("❌ Form validation failed. Errors: " + " | ".join(error_messages), "error")
        except Exception as e:
            db.session.rollback()
            flash(f"❌ An error occurred: {str(e)}", "error")

    return render_template('admin_crud.html', form=form)


@admin_bp.route('/admin/products/<int:product_id>', methods=['GET', 'POST'])
@admin_required
def edit_product(product_id):
    """Edit an existing product (Admin Only)."""
    product = Product.query.get_or_404(product_id)
    form = ProductForm(obj=product)

    if form.validate_on_submit():
        try:
            form.populate_obj(product)  # Update non-image fields

            # ✅ Upload image to S3 instead of storing as BLOB
            image_file = request.files.get('image')
            if image_file and image_file.filename:
                product.image_url = upload_file_to_s3(image_file)  # ✅ Store S3 URL

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


#@admin_bp.route('/admin/products/<int:product_id>/image')
#@admin_required
#def product_image(product_id):
#    """Serves the product image from the BLOB column."""
#
#    product = Product.query.get_or_404(product_id)
#    if not product.image_data:
#        # If the product has no BLOB data, return a 404 or a placeholder
#       abort(404, "No image for this product")

    # Return the image data as a file-like object
#    return send_file(
#        BytesIO(product.image_data),
#        mimetype='image/jpeg',  # Or detect the actual image type if you store it
#        as_attachment=False
#    )


@admin_bp.route('/admin/products/<int:product_id>/delete', methods=['POST'])
@admin_required
def delete_product(product_id):
    # Only admins can delete products

    product = Product.query.get_or_404(product_id)
    try:
        db.session.delete(product)
        db.session.commit()
        flash('Product deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting product: {str(e)}", 'error')

    return redirect(url_for('admin.dashboard'))

