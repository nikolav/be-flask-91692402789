#!/bin/bash
# waitress-serve --host 0.0.0.0 --port 5000 flask_app:app
hypercorn --host 0.0.0.0 --port 5000 flask_app_asgi:asgi_app

