
from hypercorn.middleware import AsyncioWSGIMiddleware

from flask_app import app


asgi_app = AsyncioWSGIMiddleware(app, 
                                 max_body_size = app.config['MAX_BODY_SIZE'])



