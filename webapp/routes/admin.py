import os
import boto3
from flask import request, flash, redirect, url_for, render_template, jsonify
from werkzeug.utils import secure_filename
from webapp.extensions import db
from webapp.models import Product
from webapp.forms import ProductForm
from flask_login import login_required
from flask import Blueprint
from botocore.exceptions import NoCredentialsError, ClientError

from wsgi import app

admin_bp = Blueprint('admin', __name__)

# ✅ AWS S3 Configuration for VPC Gateway Endpoint
S3_BUCKET = os.getenv("AWS_S3_BUCKET", "s3-assets-ecommerce")
S3_REGION = os.getenv("AWS_S3_REGION", "us-east-1")
S3_VPC_ENDPOINT = f"https://s3.{S3_REGION}.amazonaws.com"  # Ensure correct format

# ✅ Boto3 client using IAM Role authentication
s3_client = boto3.client(
    's3',
    endpoint_url=S3_VPC_ENDPOINT,  # Use VPC Endpoint
    region_name=S3_REGION
)

@admin_bp.route('/admin/products/new', methods=['GET'])
@login_required
def create_product_form():
    form = ProductForm()
    return render_template('admin_crud.html', form=form)


### ✅ **POST: Handle Product Creation and S3 Upload**
@admin_bp.route('/admin/products/new', methods=['POST'])
@login_required
def create_product():
    form = ProductForm()  # Initialize form object
    app.logger.info("🔹 Request received for creating a new product")

    try:
        # ✅ Log Request Headers & Form Data
        app.logger.debug(f"Headers: {request.headers}")
        app.logger.debug(f"Form Data: {request.form}")
        app.logger.debug(f"Files: {request.files}")

        # ✅ Extract Data Manually
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()
        original_price = request.form.get("original_price")
        discount_price = request.form.get("discount_price")
        stock = request.form.get("stock")

        # ✅ Log Extracted Fields
        app.logger.debug(f"Extracted Data - Name: {name}, Description: {description}, Original Price: {original_price}, Discount Price: {discount_price}, Stock: {stock}")

        # ✅ Validate Fields
        if not name or not original_price or not stock:
            flash("❌ Name, Original Price, and Stock are required fields.", "error")
            app.logger.error("⚠️ Missing required fields. Returning to form.")
            return redirect(url_for('admin.create_product_form'))

        # ✅ Convert Numeric Fields
        try:
            original_price = float(original_price)
            discount_price = float(discount_price) if discount_price else None
            stock = int(stock)
        except ValueError:
            flash("❌ Invalid price or stock value.", "error")
            app.logger.error(f"❌ Invalid numeric values: original_price={original_price}, discount_price={discount_price}, stock={stock}")
            return redirect(url_for('admin.create_product_form'))

        # ✅ Create Product Object
        product = Product(
            name=name,
            description=description,
            original_price=original_price,
            discount_price=discount_price,
            stock=stock
        )
        app.logger.info(f"✅ Product Object Created: {product}")

        # ✅ Handle Image Upload to S3
        image_file = request.files.get("image")
        if image_file and image_file.filename:
            filename = secure_filename(image_file.filename)
            s3_key = f"uploads/products/{filename}"

            try:
                app.logger.info(f"🔹 Uploading image to S3: {s3_key}")

                # ✅ Upload to S3 using VPC Endpoint
                s3_client.upload_fileobj(
                    image_file,
                    S3_BUCKET,
                    s3_key,
                    ExtraArgs={'ContentType': image_file.content_type, 'ACL': 'private'}
                )

                # ✅ Store the S3 URL in the database
                product.image_url = f"{S3_VPC_ENDPOINT}/{S3_BUCKET}/{s3_key}"
                app.logger.info(f"✅ S3 Upload Success: {product.image_url}")

            except NoCredentialsError:
                flash("❌ AWS IAM Role not detected. Ensure EC2 has an IAM Role attached.", "error")
                app.logger.error("❌ AWS IAM Role not found.")
                return redirect(url_for('admin.create_product_form'))

            except ClientError as e:
                flash(f"❌ S3 Upload Error: {str(e)}", "error")
                app.logger.error(f"❌ S3 ClientError: {str(e)}")
                return redirect(url_for('admin.create_product_form'))

        # ✅ Save Product to Database
        db.session.add(product)
        db.session.commit()
        app.logger.info(f"✅ Product Created: {product.name}")

        flash('✅ Product created successfully!', 'success')
        return redirect(url_for('admin.dashboard'))

    except Exception as e:
        db.session.rollback()
        flash(f"❌ An error occurred: {str(e)}", "error")
        app.logger.error(f"❌ Unexpected Error: {str(e)}")

    return redirect(url_for('admin.create_product_form'))



### ✅ **GET: Render the Product Edit Form**
@admin_bp.route('/admin/products/edit/<int:product_id>', methods=['GET'])
@login_required
def edit_product_form(product_id):
    product = Product.query.get_or_404(product_id)
    form = ProductForm(obj=product)
    return render_template('admin_crud.html', form=form, product=product)


### ✅ **POST: Update an Existing Product**
@admin_bp.route('/admin/products/edit/<int:product_id>', methods=['POST'])
@login_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    form = ProductForm()

    try:
        if form.validate_on_submit():
            product.name = form.name.data
            product.description = form.description.data
            product.original_price = form.original_price.data
            product.discount_price = form.discount_price.data
            product.stock = form.stock.data

            # ✅ Handle Image Upload to S3 (If new image is provided)
            image_file = request.files.get('image')
            if image_file and image_file.filename:
                filename = secure_filename(image_file.filename)
                s3_key = f"uploads/products/{filename}"

                # ✅ Upload to S3 using VPC Endpoint
                s3_client.upload_fileobj(
                    image_file,
                    S3_BUCKET,
                    s3_key,
                    ExtraArgs={'ContentType': image_file.content_type, 'ACL': 'private'}
                )

                # ✅ Update the product image URL in the database
                product.image_url = f"{S3_VPC_ENDPOINT}/{S3_BUCKET}/{s3_key}"

            db.session.commit()

            flash('Product updated successfully!', 'success')
            return redirect(url_for('admin.dashboard'))

    except NoCredentialsError:
        flash("AWS IAM Role not detected. Ensure EC2 has an IAM Role attached.", 'error')

    except ClientError as e:
        flash(f"S3 Upload Error: {str(e)}", 'error')

    except Exception as e:
        db.session.rollback()
        flash(f"An error occurred: {str(e)}", 'error')

    return redirect(url_for('admin.edit_product_form', product_id=product.id))


### ✅ **DELETE: Delete a Product**
@admin_bp.route('/admin/products/delete/<int:product_id>', methods=['POST'])
@login_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)

    try:
        # ✅ Remove product from database
        db.session.delete(product)
        db.session.commit()

        flash('Product deleted successfully!', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f"An error occurred: {str(e)}", 'error')

    return redirect(url_for('admin.dashboard'))


### ✅ **GET: View All Products (Admin Dashboard)**
@admin_bp.route('/admin/dashboard', methods=['GET'])
@login_required
def dashboard():
    products = Product.query.order_by(Product.created_at.desc()).all()
    return render_template('admin_dashboard.html', products=products)
