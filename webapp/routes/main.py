from flask import Blueprint, jsonify, render_template
from webapp.extensions import db

main_bp = Blueprint('main', __name__)

@main_bp.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'database': 'connected' if db.session.connection() else 'disconnected'
    })

@main_bp.route('/')
def home():
    # Render the home.html template
    return render_template('home.html')