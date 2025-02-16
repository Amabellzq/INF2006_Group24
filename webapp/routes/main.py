import os
import boto3
from flask import Blueprint, jsonify, render_template
from webapp.models import Product
from webapp.extensions import db
from botocore.exceptions import NoCredentialsError, ClientError

# Define Flask Blueprint
main_bp = Blueprint('main', __name__)

# AWS S3 Configuration for VPC Gateway Endpoint
S3_BUCKET = os.getenv("AWS_S3_BUCKET", "s3-assets-ecommerce")
S3_REGION = os.getenv("AWS_S3_REGION", "us-east-1")
S3_VPC_ENDPOINT = f"https://s3.{S3_REGION}.amazonaws.com"  # ✅ Ensure correct format

# ✅ Boto3 client using IAM Role authentication (No access keys needed)
s3_client = boto3.client(
    's3',
    endpoint_url=S3_VPC_ENDPOINT,  # ✅ Use VPC Endpoint
    region_name=S3_REGION
)


# ✅ Health Check Route
@main_bp.route('/health')
def health_check():
    try:
        db.session.connection()
        return jsonify({'status': 'healthy', 'database': 'connected'}), 200
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'database': 'disconnected', 'error': str(e)}), 500


# ✅ Homepage Route
@main_bp.route('/')
def home():
    """Fetch all products and separate Flash Deals from regular products."""

    # Flash Deals: Products that have a discount price
    flash_deals = Product.query.filter(
        Product.discount_price.isnot(None)
    ).order_by(Product.created_at.desc()).all()

    # Regular Products: Products that do NOT have a discount price
    products = Product.query.filter(
        Product.discount_price.is_(None)
    ).order_by(Product.created_at.desc()).all()

    return render_template('home.html', flash_deals=flash_deals, products=products)


# ✅ About Page Route
@main_bp.route('/about')
def about():
    return render_template('about.html')


# ✅ Route to Create and Upload File to S3
@main_bp.route('/create-upload', methods=['GET'])
def create_and_upload_file():
    try:
        # ✅ Step 1: Create a new file locally
        file_path = "newtestfile.txt"
        file_content = "This is a test file uploaded to S3 via Flask."

        with open(file_path, "w") as file:
            file.write(file_content)

        # ✅ Step 2: Upload file to S3
        s3_key = f"uploads/newtestfile.txt"  # Folder path in S3

        with open(file_path, "rb") as file:
            s3_client.upload_fileobj(
                file,
                S3_BUCKET,
                s3_key,
                ExtraArgs={"ContentType": "text/plain", "ACL": "private"}  # Use 'public-read' if needed
            )

        # ✅ Step 3: Construct the S3 URL
        file_url = f"{S3_VPC_ENDPOINT}/{S3_BUCKET}/{s3_key}"

        # ✅ Step 4: Delete the local file after upload
        os.remove(file_path)

        return jsonify({
            "message": "File created and uploaded successfully!",
            "file_url": file_url
        }), 200

    except NoCredentialsError:
        return jsonify({"error": "AWS IAM Role not detected. Ensure EC2 has an IAM Role attached."}), 403

    except ClientError as e:
        return jsonify({"error": f"S3 Upload Error: {str(e)}"}), 500

    except Exception as e:
        return jsonify({"error": f"Unexpected Error: {str(e)}"}), 500
