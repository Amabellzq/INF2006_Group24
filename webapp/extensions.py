# webapp/extensions.py
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_marshmallow import Marshmallow

# Initialize S3 Client using IAM Role authentication
s3 = boto3.client("s3")

db = SQLAlchemy()
migrate = Migrate()
cors = CORS()
ma = Marshmallow()
login_manager = LoginManager()
