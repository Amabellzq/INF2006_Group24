# webapp/routes/products.py
from flask import Blueprint, request, render_template
from webapp.models.product import Product
from datetime import datetime
from sqlalchemy import or_

product_bp = Blueprint('products', __name__)

@product_bp.route('/products')
def product_list():
    search = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)
    per_page = 20

    query = Product.query
    if search:
        query = query.filter(
            or_(
                Product.name.ilike(f'%{search}%'),
                Product.description.ilike(f'%{search}%')
            )
        )

    pagination = query.paginate(page=page, per_page=per_page)
    return render_template(
        'product_list.html',
        products=pagination.items,
        pagination=pagination,
        search=search
    )

@product_bp.route('/products/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
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
