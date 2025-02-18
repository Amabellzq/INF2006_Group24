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


### ✅ **GET: Render the Product Form (Create)**
import logging
from werkzeug.utils import secure_filename

# ✅ Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def list_s3_images():
    """Fetch the list of images from the S3 bucket inside 'uploads/products/'."""
    try:
        response = s3_client.list_objects_v2(Bucket=S3_BUCKET, Prefix="uploads/products/")
        image_urls = [
            f"{S3_VPC_ENDPOINT}/{S3_BUCKET}/{obj['Key']}"
            for obj in response.get('Contents', [])
            if obj['Key'].lower().endswith(('jpg', 'jpeg', 'png'))
        ]
        return image_urls
    except ClientError as e:
        flash(f"Error fetching images: {e}", "error")
        return []


### ✅ **Render the Product Form (Create)**
@admin_bp.route('/admin/products/new', methods=['GET'])
@login_required
def create_product_form():
    """Fetch list of images from S3 and render product creation form."""
    s3_images = list_s3_images()
    form = ProductForm()
    return render_template('admin_crud.html', form=form, s3_images=s3_images)




@admin_bp.route('/admin/products/new', methods=['POST'])
@login_required
def create_product():
    form = ProductForm(request.form)

    # ✅ Validate form submission
    if not form.validate_on_submit():
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{field}: {error}", "error")
        return redirect(url_for('admin.create_product_form'))

    try:
        # ✅ Extract data and validate
        name = form.name.data.strip()
        description = form.description.data.strip()
        original_price = form.original_price.data
        discount_price = form.discount_price.data
        stock = form.stock.data
        image_url = form.image_url.data  # ✅ Use selected S3 image URL

        if not name or not original_price or not stock:
            flash("❌ Name, Original Price, and Stock are required fields.", "error")
            return redirect(url_for('admin.create_product_form'))

        # ✅ Ensure numeric fields are valid
        try:
            original_price = float(original_price)
            discount_price = float(discount_price) if discount_price else None
            stock = int(stock)
        except ValueError:
            flash("❌ Invalid price or stock value!", "error")
            return redirect(url_for('admin.create_product_form'))

        # ✅ Create Product Object
        product = Product(
            name=name,
            description=description,
            original_price=original_price,
            discount_price=discount_price,
            stock=stock,
            image_url=image_url  # ✅ Store selected S3 image URL
        )

        db.session.add(product)
        db.session.commit()

        flash("✅ Product created successfully!", "success")
        return redirect(url_for('admin.dashboard'))

    except Exception as e:
        db.session.rollback()
        flash(f"❌ Unexpected Error: {str(e)}", "error")
        return redirect(url_for('admin.create_product_form'))

### ✅ **GET: Render the Product Edit Form**
@admin_bp.route('/admin/products/edit/<int:product_id>', methods=['GET'])
@login_required
def edit_product_form(product_id):
    """Fetch product details and available S3 images for editing."""
    product = Product.query.get_or_404(product_id)
    s3_images = list_s3_images()
    form = ProductForm(obj=product)
    return render_template('admin_crud.html', form=form, product=product, s3_images=s3_images)



### ✅ **POST: Update an Existing Product**
### ✅ **POST: Update an Existing Product**
@admin_bp.route('/admin/products/edit/<int:product_id>', methods=['POST'])
@login_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    form = ProductForm(request.form)

    if not form.validate_on_submit():
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{field}: {error}", "error")
        return redirect(url_for('admin.edit_product_form', product_id=product_id))

    try:
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

            try:
                s3_client.upload_fileobj(
                    image_file,
                    S3_BUCKET,
                    s3_key,
                    ExtraArgs={'ContentType': image_file.content_type, 'ACL': 'private'}
                )

                product.image_url = f"{S3_VPC_ENDPOINT}/{S3_BUCKET}/{s3_key}"

            except (NoCredentialsError, ClientError) as e:
                flash(f"❌ S3 Upload Error: {str(e)}", "error")
                return redirect(url_for('admin.edit_product_form', product_id=product_id))

        db.session.commit()

        flash("✅ Product updated successfully!", "success")
        return redirect(url_for('admin.dashboard'))

    except Exception as e:
        db.session.rollback()
        flash(f"❌ Unexpected Error: {str(e)}", "error")
        return redirect(url_for('admin.edit_product_form', product_id=product_id))


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
