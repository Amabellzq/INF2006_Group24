# webapp/routes/products.py
from io import BytesIO

from flask import Blueprint, request, render_template, abort, send_file, jsonify, url_for
from webapp.models.product import Product
from datetime import datetime
from sqlalchemy import or_

product_bp = Blueprint('products', __name__)

@product_bp.route('/products')
def product_list():
    products = Product.query.all()
    return render_template('product_list.html', products=products)

@product_bp.route('/products/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('product_detail.html', product=product)

@product_bp.route('/products/<int:product_id>/image')
def product_image(product_id):
    product = Product.query.get_or_404(product_id)
    if not product.image_data:
        # Fallback or 404
        abort(404, "No image data.")
    return send_file(
        BytesIO(product.image_data),
        mimetype='image/jpeg',  # or detect the actual type
        as_attachment=False
    )


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

    # Perform a case-insensitive search on product name and description
    products = Product.query.filter(
        or_(
            Product.name.ilike(f'%{query}%'),
            Product.description.ilike(f'%{query}%')
        )
    ).all()

    # Format the results for JSON response
    results = [
        {
            "name": product.name,
            "description": product.description,
            "original_price": str(product.original_price),
            "discount_price": str(product.discount_price) if product.discount_price else str(product.original_price),
            "stock": product.stock,
            "is_flash_deal": product.is_flash_sale,
            "image": url_for('products.product_image', product_id=product.id),
            "url": url_for('products.product_detail', product_id=product.id)
        } for product in products
    ]

    return jsonify({"results": results})