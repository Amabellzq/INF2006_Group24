from flask import Blueprint, request, render_template, abort, send_file, jsonify, url_for, Response
from webapp.models.product import Product
from datetime import datetime
from sqlalchemy import or_
import boto3
import io

product_bp = Blueprint('products', __name__)

# Initialize S3 client
s3_client = boto3.client("s3")
S3_BUCKET = "s3-assets-ecommerce"

import re


def extract_s3_key(image_url):
    """Extracts the S3 object key from the full S3 URL."""
    if not image_url:
        return None
    match = re.search(rf"{S3_BUCKET}/(.+)", image_url)
    return match.group(1) if match else None


@product_bp.route('/products/<int:product_id>/image')
def product_image(product_id):
    """Retrieve and serve an image from S3 via VPC Gateway Endpoint."""
    global s3_key
    product = Product.query.get_or_404(product_id)

    if not product.image_url:
        abort(404, "No image available.")

    try:
        # Log product image URL for debugging
        print(f"📸 Fetching image for product {product_id}: {product.image_url}")

        # Extract the correct S3 key
        s3_key = extract_s3_key(product.image_url)
        if not s3_key:
            print(f"Invalid S3 Key Extracted for {product.image_url}")
            abort(400, "Invalid S3 Key.")

        print(f"Extracted S3 Key: {s3_key}")

        # Fetch image from S3 via VPC Gateway
        s3_response = s3_client.get_object(Bucket=S3_BUCKET, Key=s3_key)

        image_data = s3_response["Body"].read()
        content_type = s3_response["ContentType"]

        return Response(image_data, mimetype=content_type)

    except s3_client.exceptions.NoSuchKey:
        print(f"S3 Object Not Found: {s3_key}")
        abort(404, "Image not found in S3.")
    except Exception as e:
        print(f"Error fetching image: {str(e)}")
        abort(500, f"Internal Server Error: {str(e)}")


@product_bp.route('/products')
def product_list():
    products = Product.query.all()
    return render_template('product_list.html', products=products)


@product_bp.route('/products/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)

    if product.discount_price is None:
        product.discount_price = product.original_price

    return render_template('product_detail.html', product=product)


@product_bp.route('/products/flash-sale')
def flash_sale():
    now = datetime.utcnow()
    products = Product.query.filter(
        Product.is_flash_sale == True,
        Product.flash_sale_start <= now,
        Product.flash_sale_end >= now
    ).all()
    return render_template('product_list.html', products=products, flash_sale=True)


@product_bp.route('/search')
def search():
    query = request.args.get('query', '').strip()

    if not query:
        return jsonify({"results": []})

    # Perform case-insensitive search on product name and description
    products = Product.query.filter(
        or_(
            Product.name.ilike(f'%{query}%'),
            Product.description.ilike(f'%{query}%')
        )
    ).all()

    # Format results for JSON response, ensuring discount_price is never None
    results = [
        {
            "name": product.name,
            "description": product.description,
            "original_price": str(product.original_price),
            "discount_price": str(product.discount_price) if product.discount_price is not None else str(
                product.original_price),
            "stock": product.stock,
            "is_flash_deal": product.is_flash_sale,
            "image": url_for('products.product_image',
                             product_id=product.id) if product.image_url else "https://via.placeholder.com/400x300?text=No+Image",
            "url": url_for('products.product_detail', product_id=product.id)
        } for product in products
    ]

    return jsonify({"results": results})
