import os
import boto3
import random
import logging
from datetime import datetime, timedelta
from flask import Blueprint, jsonify, render_template
from sqlalchemy import text

from webapp.models import Product
from webapp.extensions import db, get_cache_data
from botocore.exceptions import NoCredentialsError, ClientError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


main_bp = Blueprint('main', __name__)

S3_BUCKET = os.getenv("AWS_S3_BUCKET", "s3-assets-ecommerce")
S3_REGION = os.getenv("AWS_S3_REGION", "us-east-1")
S3_VPC_ENDPOINT = f"https://s3.{S3_REGION}.amazonaws.com"  # ✅ Ensure correct format

s3_client = boto3.client(
    's3',
    endpoint_url=S3_VPC_ENDPOINT,  # ✅ Use VPC Endpoint
    region_name=S3_REGION
)


@main_bp.route('/health')
def health_check():
    try:
        db.session.connection()
        return jsonify({'status': 'healthy', 'database': 'connected'}), 200
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        return jsonify({'status': 'unhealthy', 'database': 'disconnected', 'error': str(e)}), 500

# @main_bp.route('/')
# def home():
#     """Fetch all products and separate Flash Deals from regular products."""

#     # Flash Deals: Products that have a discount price
#     flash_deals = Product.query.filter(
#         Product.discount_price.isnot(None)
#     ).order_by(Product.created_at.desc()).all()

#     # Regular Products: Products that do NOT have a discount price
#     products = Product.query.filter(
#         Product.discount_price.is_(None)
#     ).order_by(Product.created_at.desc()).all()


#     return render_template('home.html', flash_deals=flash_deals, products=products)

@main_bp.route('/')
def home():
    """Fetch all products and separate Flash Deals from regular products with caching."""

    def fetch_homepage_data():
        flash_deals = Product.query.filter(Product.discount_price.isnot(None)).order_by(Product.created_at.desc()).all()
        products = Product.query.filter(Product.discount_price.is_(None)).order_by(Product.created_at.desc()).all()

        return {
            "flash_deals": [product.to_dict() for product in flash_deals],
            "products": [product.to_dict() for product in products]
        }

    # Retrieve homepage data from cache or database
    homepage_data = get_cache_data("homepage_data", fetch_homepage_data, expiration=600)

    return render_template(
        'home.html',
        flash_deals=homepage_data["flash_deals"],
        products=homepage_data["products"]
    )

@main_bp.route('/about')
def about():
    return render_template('about.html')


@main_bp.route('/create-upload', methods=['GET'])
def create_and_upload_file():
    try:
        file_path = "newtestfile.txt"
        file_content = "This is a test file uploaded to S3 via Flask."

        with open(file_path, "w") as file:
            file.write(file_content)

        s3_key = f"uploads/newtestfile.txt"  # Folder path in S3

        with open(file_path, "rb") as file:
            s3_client.upload_fileobj(
                file,
                S3_BUCKET,
                s3_key,
                ExtraArgs={"ContentType": "text/plain", "ACL": "private"}  # Use 'public-read' if needed
            )

        file_url = f"{S3_VPC_ENDPOINT}/{S3_BUCKET}/{s3_key}"

        os.remove(file_path)

        return jsonify({
            "message": "File created and uploaded successfully!",
            "file_url": file_url
        }), 200

    except NoCredentialsError:
        logger.error("AWS IAM Role not detected. Ensure EC2 has an IAM Role attached.")
        return jsonify({"error": "AWS IAM Role not detected. Ensure EC2 has an IAM Role attached."}), 403

    except ClientError as e:
        logger.error(f"S3 Upload Error: {str(e)}")
        return jsonify({"error": f"S3 Upload Error: {str(e)}"}), 500

    except Exception as e:
        logger.error(f"Unexpected Error: {str(e)}")
        return jsonify({"error": f"Unexpected Error: {str(e)}"}), 500


@main_bp.route('/insert-fake-products', methods=['GET'])
def insert_fake_products():
    try:
        fake_products = [
            {
                "name": "Wireless Headphones",
                "description": "High-quality wireless headphones with noise cancellation.",
                "original_price": 120.00,
                "discount_price": 90.00,
                "stock": 50
            },
            {
                "name": "Smartwatch Series 5",
                "description": "Feature-rich smartwatch with fitness tracking.",
                "original_price": 199.99,
                "discount_price": 159.99,
                "stock": 30
            },
            {
                "name": "Gaming Mouse",
                "description": "RGB gaming mouse with adjustable DPI.",
                "original_price": 49.99,
                "discount_price": None,
                "stock": 100
            }
        ]

        local_image_path = "webapp/static/media/BannerAbout.png"
        if not os.path.exists(local_image_path):
            logger.error(" Error: BannerAbout.png file not found!")
            return jsonify({"error": "BannerAbout.png file not found!"}), 404

        s3_key = f"uploads/products/BannerAbout.png"

        with open(local_image_path, "rb") as image_file:
            s3_client.upload_fileobj(
                image_file,
                S3_BUCKET,
                s3_key,
                ExtraArgs={'ContentType': 'image/png', 'ACL': 'private'}
            )

        #  Store the S3 Image URL
        image_url = f"{S3_VPC_ENDPOINT}/{S3_BUCKET}/{s3_key}"

        #  Insert Products into Database
        for fake in fake_products:
            product = Product(
                name=fake["name"],
                description=fake["description"],
                original_price=fake["original_price"],
                discount_price=fake["discount_price"],
                stock=fake["stock"],
                image_url=image_url,  #  Use the uploaded S3 image
                is_flash_sale=random.choice([True, False]),
                flash_sale_start=datetime.utcnow() if random.choice([True, False]) else None,
                flash_sale_end=datetime.utcnow() + timedelta(days=1) if random.choice([True, False]) else None,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.session.add(product)

        db.session.commit()
        logger.info(" Fake products inserted successfully!")

        return jsonify({
            "message": " Fake products inserted successfully!",
            "image_url": image_url
        }), 201

    except NoCredentialsError:
        logger.error("AWS IAM Role not detected. Ensure EC2 has an IAM Role attached.")
        return jsonify({"error": "AWS IAM Role not detected. Ensure EC2 has an IAM Role attached."}), 403

    except ClientError as e:
        logger.error(f"S3 Upload Error: {str(e)}")
        return jsonify({"error": f"S3 Upload Error: {str(e)}"}), 500

    except Exception as e:
        db.session.rollback()
        logger.error(f"Unexpected Error: {str(e)}")
        return jsonify({"error": f"Unexpected Error: {str(e)}"}), 500

@main_bp.route('/check-db')
def check_db():
    try:
        with db.session.connection() as conn:
            result = conn.execute(text("SELECT @@hostname")).fetchone()
        return jsonify({"Using Database": result[0] if result else "Unknown"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

