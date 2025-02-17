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


def generate_presigned_url(s3_key, expiration=3600):
    """ Generate a presigned URL for accessing S3 objects. """
    try:
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': S3_BUCKET, 'Key': s3_key},
            ExpiresIn=expiration
        )
        return url
    except Exception as e:
        print(f"❌ Error generating presigned URL: {e}")
        return None


@product_bp.route('/products')
def product_list():
    products = Product.query.all()
    for product in products:
        if product.image_url:
            product.image_url = generate_presigned_url(product.image_url)
    return render_template('product_list.html', products=products)


@product_bp.route('/products/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)

    # Ensure discount_price is not None
    if product.discount_price is None:
        product.discount_price = product.original_price

    if product.image_url:
        product.image_url = generate_presigned_url(product.image_url)

    return render_template('product_detail.html', product=product)


@product_bp.route('/products/flash-sale')
def flash_sale():
    now = datetime.utcnow()
    products = Product.query.filter(
        Product.is_flash_sale == True,
        Product.flash_sale_start <= now,
        Product.flash_sale_end >= now
    ).all()
    for product in products:
        if product.image_url:
            product.image_url = generate_presigned_url(product.image_url)
    return render_template('product_list.html', products=products, flash_sale=True)


@product_bp.route('/search')
def search():
    query = request.args.get('query', '').strip()

    if not query:
        return jsonify({"results": []})

    # ✅ Perform case-insensitive search on product name and description
    products = Product.query.filter(
        or_(
            Product.name.ilike(f'%{query}%'),
            Product.description.ilike(f'%{query}%')
        )
    ).all()

    # ✅ Format results for JSON response, ensuring discount_price is never None
    results = [
        {
            "name": product.name,
            "description": product.description,
            "original_price": str(product.original_price),
            "discount_price": str(product.discount_price) if product.discount_price is not None else str(
                product.original_price),
            "stock": product.stock,
            "is_flash_deal": product.is_flash_sale,
            "image": generate_presigned_url(
                product.image_url) if product.image_url else "https://via.placeholder.com/400x300?text=No+Image",
            "url": url_for('products.product_detail', product_id=product.id)
        } for product in products
    ]

    return jsonify({"results": results})
