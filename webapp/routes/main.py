from flask import Blueprint, jsonify, render_template
from webapp.extensions import db

main_bp = Blueprint('main', __name__)

@main_bp.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'database': 'connected' if db.session.connection() else 'disconnected'
    })


from flask import Blueprint, render_template
from webapp.models import Product
from webapp.extensions import db

main_bp = Blueprint('main', __name__)


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