# webapp/models/user.py
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from webapp.extensions import db
from sqlalchemy import event


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.Enum('user', 'admin'), default='user', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    active = db.Column(db.Boolean, default=True, nullable=False)
    version_id = db.Column(db.Integer, nullable=False, default=0)

    __mapper_args__ = {
        "version_id_col": version_id
    }

    # Relationships
    cart = db.relationship('Cart', back_populates='user', uselist=False, cascade='all, delete')
    orders = db.relationship('Order', back_populates='user', cascade='all, delete')

    __table_args__ = (
        db.Index('ix_users_email', 'email', mysql_length=120),
        db.CheckConstraint('email LIKE "%@%"', name='valid_email'),
        db.Index('ix_users_active', 'active'),
    )

    def set_password(self, password):
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters")
        self.password_hash = generate_password_hash(
            password,
            method='scrypt',
            salt_length=16
        )

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return self.active

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'role': self.role,
            'created_at': self.created_at.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None
        }


@event.listens_for(User, 'before_update')
def update_version(mapper, connection, target):
    target.version_id += 1


