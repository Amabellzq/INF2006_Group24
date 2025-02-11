from functools import wraps
from flask import flash, redirect, url_for
from flask_login import login_required, current_user

def admin_required(f):
    """Decorator to restrict access to admin users only."""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash("Unauthorized access! Admins only.", "error")
            return redirect(url_for('main.home'))
        return f(*args, **kwargs)
    return decorated_function
