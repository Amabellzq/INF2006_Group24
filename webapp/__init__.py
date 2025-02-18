import redis
from flask_session import Session
from webapp.config import Config
from flask import Flask, g, request
from webapp.extensions import db, migrate, ma, login_manager
from webapp.errors import (
    handle_validation_error,
    handle_http_error,
    handle_db_error,
    handle_concurrent_update
)
from webapp.models import User

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    login_manager.init_app(app)
    
    app.config['SESSION_REDIS'] = redis.from_url(
        app.config['REDIS_URL'],
        ssl=True
    )
    @app.before_request
    def set_db_bind():
        """Automatically bind read queries to the read replica."""
        g.db_bind = "read_replica" if request.method == "GET" else None
        
    app.config['WTF_CSRF_HEADERS'] = ['X-CSRFToken', 'X-XSRF-TOKEN']
    Session(app)




    # User loader function
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    #cors.init_app(app, resources={r"/*": {"origins": app.config['CORS_ORIGINS']}})
    ma.init_app(app)

    # Register error handlers
    app.register_error_handler(400, handle_validation_error)
    app.register_error_handler(401, handle_http_error(401))
    app.register_error_handler(403, handle_http_error(403))
    app.register_error_handler(404, handle_http_error(404))
    app.register_error_handler(409, handle_concurrent_update)
    app.register_error_handler(500, handle_db_error)

    # Register blueprints
    from webapp.routes.auth import auth_bp
    from webapp.routes.products import product_bp
    from webapp.routes.orders import order_bp
    from webapp.routes.admin import admin_bp
    from webapp.routes.payment import payment_bp
    from webapp.routes.main import main_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(product_bp)
    app.register_blueprint(order_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(payment_bp)

    # Only create tables in **Development Mode**
    if app.config['DEBUG']:
        with app.app_context():
            db.create_all()

    return app
