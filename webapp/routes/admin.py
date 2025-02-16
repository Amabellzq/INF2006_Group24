import os
import boto3
from flask import request, flash, redirect, url_for, render_template
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

@admin_bp.route('/admin/products/new', methods=['GET', 'POST'])
@login_required
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

                # ✅ Handle Image Upload to S3
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

                    # ✅ Store the S3 URL in the database
                    product.image_url = f"{S3_VPC_ENDPOINT}/{S3_BUCKET}/{s3_key}"

                db.session.add(product)
                db.session.commit()

                flash('Product created successfully!', 'success')
                return redirect(url_for('admin.dashboard'))

            else:
                # Collect and flash individual errors
                error_messages = []
                for field, errors in form.errors.items():
                    for error in errors:
                        error_messages.append(f"{field}: {error}")

                if error_messages:
                    flash("Form validation failed. Errors: " + " | ".join(error_messages), 'error')

        except NoCredentialsError:
            flash("AWS IAM Role not detected. Ensure EC2 has an IAM Role attached.", 'error')

        except ClientError as e:
            flash(f"S3 Upload Error: {str(e)}", 'error')

        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred: {str(e)}", 'error')

    return render_template('admin_crud.html', form=form)
