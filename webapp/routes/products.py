# # webapp/routes/products.py
# from io import BytesIO
import os
# from flask import Blueprint, request, render_template, abort, send_file, jsonify, url_for
# from webapp.models.product import Product
# from datetime import datetime
# from sqlalchemy import or_

# product_bp = Blueprint('products', __name__)

# @product_bp.route('/products')
# def product_list():
#     products = Product.query.all()
#     return render_template('product_list.html', products=products)

# @product_bp.route('/products/<int:product_id>')
# def product_detail(product_id):
#     product = Product.query.get_or_404(product_id)

#     # ✅ Ensure discount_price is a valid number, fallback to original_price
#     discount_price = product.discount_price if product.discount_price is not None else product.original_price

#     return render_template('product_detail.html', product=product)

# @product_bp.route('/products/<int:product_id>/image')
# def product_image(product_id):
#     product = Product.query.get_or_404(product_id)
#     if not product.image_data:
#         # Fallback or 404
#         abort(404, "No image data.")
#     return send_file(
#         BytesIO(product.image_data),
#         mimetype='image/jpeg',  # or detect the actual type
#         as_attachment=False
#     )


# @product_bp.route('/products/flash-sale')
# def flash_sale():
#     now = datetime.utcnow()
#     products = Product.query.filter(
#         Product.is_flash_sale == True,
#         Product.flash_sale_start <= now,
#         Product.flash_sale_end >= now
#     ).all()
#     return render_template('product_list.html', products=products, flash_sale=True)

# @product_bp.route('/search')
# def search():
#     query = request.args.get('query', '').strip()

#     if not query:
#         return jsonify({"results": []})

#     # Perform a case-insensitive search on product name and description
#     products = Product.query.filter(
#         or_(
#             Product.name.ilike(f'%{query}%'),
#             Product.description.ilike(f'%{query}%')
#         )
#     ).all()

#     # Format the results for JSON response
#     results = [
#         {
#             "name": product.name,
#             "description": product.description,
#             "original_price": str(product.original_price),
#             "discount_price": str(product.discount_price) if product.discount_price else str(product.original_price),
#             "stock": product.stock,
#             "is_flash_deal": product.is_flash_sale,
#             "image": url_for('products.product_image', product_id=product.id),
#             "url": url_for('products.product_detail', product_id=product.id)
#         } for product in products
#     ]

#     return jsonify({"results": results})

# webapp/routes/products.py
from io import BytesIO

import boto3
from flask import Blueprint, request, render_template, abort, send_file, jsonify, url_for, Response
from webapp.models.product import Product
from datetime import datetime
from sqlalchemy import or_



product_bp = Blueprint('products', __name__)
# ✅ AWS S3 Configuration for VPC Gateway Endpoint
S3_BUCKET = os.getenv("AWS_S3_BUCKET", "s3-assets-ecommerce")
S3_REGION = os.getenv("AWS_S3_REGION", "us-east-1")
S3_VPC_ENDPOINT = f"https://s3.{S3_REGION}.amazonaws.com"  # ✅ Ensure correct format

# ✅ Boto3 client using IAM Role authentication (No access keys needed)
s3_client = boto3.client(
    's3',
    endpoint_url=S3_VPC_ENDPOINT,  # ✅ Use VPC Endpoint
    region_name=S3_REGION
)

@product_bp.route('/products')
def product_list():
    products = Product.query.all()
    return render_template('product_list.html', products=products)

@product_bp.route('/products/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)

    # Ensure discount_price is not None
    if product.discount_price is None:
        product.discount_price = product.original_price

    return render_template('product_detail.html', product=product)


@product_bp.route('/products/<int:product_id>/image')
def product_image(product_id):
    product = Product.query.get_or_404(product_id)
    if not product.image_url:
        abort(404, "No image available.")

    try:
        # Fetch image from S3 via VPC Endpoint
        s3_response = s3_client.get_object(Bucket=S3_BUCKET, Key=product.image_url)
        image_data = s3_response["Body"].read()
        content_type = s3_response["ContentType"]
        return Response(image_data, mimetype=content_type)

    except s3_client.exceptions.NoSuchKey:
        abort(404, "Image not found in S3.")
    except Exception as e:
        abort(500, f"Error fetching image: {str(e)}")


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
            "discount_price": str(product.discount_price) if product.discount_price is not None else str(product.original_price),
            "stock": product.stock,
            "is_flash_deal": product.is_flash_sale,
            "image": url_for('products.product_image', product_id=product.id),
            "url": url_for('products.product_detail', product_id=product.id)
        } for product in products
    ]

    return jsonify({"results": results})
