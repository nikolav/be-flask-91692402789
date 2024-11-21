
from hypercorn.middleware import AsyncioWSGIMiddleware

from flask_app import app


asgi_app = AsyncioWSGIMiddleware(app)
