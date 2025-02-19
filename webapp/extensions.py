# webapp/extensions.py
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow
import redis

db = SQLAlchemy()
migrate = Migrate()
#cors = CORS()
ma = Marshmallow()
login_manager = LoginManager()

# ElastiCache (Valkey) Configuration
VALKEY_HOST = "my-valkey-cache-nf0k1b.serverless.use1.cache.amazonaws.com"
VALKEY_PORT = 6379

# Connect to ElastiCache (Valkey)
cache = redis.StrictRedis(host=VALKEY_HOST, port=VALKEY_PORT, decode_responses=True)

def get_cache_data(key, fallback_function, expiration=300):
    """
    Fetch data from cache or call the fallback function if not cached.
    Expiration time is set to 5 minutes (300 seconds) by default.
    """
    data = cache.get(key)
    if data:
        print(f"Cache hit: {key}")
        return eval(data)  # Convert stored string back to dictionary
    else:
        print(f"Cache miss: {key}")
        result = fallback_function()
        cache.setex(key, expiration, str(result))  # Store data in cache
        return result


# Function to execute queries (automatically uses Read Replica for GET requests)
def query_db(sql, params=None):
    bind = g.get("db_bind", None)  # Use read replica for GET requests
    return db.session.execute(sql, params or {}, bind=bind).fetchall()
