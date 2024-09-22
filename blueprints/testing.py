from flask      import Blueprint
from flask_cors import CORS

bp_testing = Blueprint('testing', __name__, url_prefix = '/test')

# cors blueprints as wel for cross-domain requests
CORS(bp_testing)


@bp_testing.route('/', methods = ('POST',))
def testing_home():    
  from flask import g
  from servcies.firebase.messaging import send
  from datetime import datetime
  from datetime import timezone
  send(
    tokens  = g.user.cloud_messaging_device_tokens(),
    payload = {'title': 'fcm:demo:2', 'body': str(datetime.now(tz = timezone.utc))}
  )
  return []
