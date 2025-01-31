# webapp/routes/__init__.py
from .main import main_bp
from .auth import auth_bp
from .products import product_bp
from .orders import order_bp
from .admin import  admin_bp
from .payment import  payment_bp
from .cart import  cart_bp


__all__ = ['main_bp', 'auth_bp', 'product_bp', 'order_bp', 'admin_bp', 'payment_bp' , 'cart_bp']