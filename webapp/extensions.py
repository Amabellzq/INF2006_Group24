# webapp/extensions.py
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow
import redis
from redis import Redis

db = SQLAlchemy()
migrate = Migrate()
#cors = CORS()
ma = Marshmallow()
login_manager = LoginManager()

# Initialize Redis Cache (Valkey) from Flask config
cache = None

def init_cache(app):
    global cache
    redis_url = app.config.get("REDIS_URL")
    if redis_url:
        cache = Redis.from_url(redis_url, decode_responses=True)
    else:
        print("⚠️ Warning: No REDIS_URL provided, caching will be disabled.")

# Cache Utility Function
def get_cache_data(key, fallback_function, expiration=300):
    """
    Fetch data from cache or call the fallback function if not cached.
    """
    if cache is None:
        return fallback_function()  # Return fresh data if caching is disabled

    data = cache.get(key)
    if data:
        print(f"✅ Cache HIT for: {key}")  # Log cache hit
        return eval(data)
    else:
        print(f"❌ Cache MISS for: {key}")  # Log cache miss
        result = fallback_function()
        cache.setex(key, expiration, str(result))  # Cache the result
        return result

# Function to execute queries (automatically uses Read Replica for GET requests)
def query_db(sql, params=None):
    bind = g.get("db_bind", None)  # Use read replica for GET requests
    return db.session.execute(sql, params or {}, bind=bind).fetchall()
