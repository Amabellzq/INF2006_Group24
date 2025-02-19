# webapp/extensions.py
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow

db = SQLAlchemy()
migrate = Migrate()
#cors = CORS()
ma = Marshmallow()
login_manager = LoginManager()


# Function to execute queries (automatically uses Read Replica for GET requests)
def query_db(sql, params=None):
    bind = g.get("db_bind", None)  # Use read replica for GET requests
    return db.session.execute(sql, params or {}, bind=bind).fetchall()
