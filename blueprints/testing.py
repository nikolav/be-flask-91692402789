from flask      import Blueprint
from flask_cors import CORS

bp_testing = Blueprint('testing', __name__, url_prefix = '/test')

# cors blueprints as wel for cross-domain requests
CORS(bp_testing)


@bp_testing.route('/', methods = ('POST',))
def testing_home():    
  from servcies.firebase.messaging import send
  from datetime import datetime
  from datetime import timezone
  send(
    tokens  = ['duxCWVRBOd6TVpTa5Owm-x:APA91bGeavyRk4gYcs--3l9QLz3KwBxFa4CN9oJUS9pUmKHQrqOcqU6E6MOIiMHNMmNg2Oh7T2VjYrmnxiHlJeWtsmUBGz055c0-gwiE7WP1lepIZ2qFkuXfcTlQb2mtSF9hKNiO5m1v'],
    payload = {'title': 'fcm:demo', 'body': str(datetime.now(tz = timezone.utc))}
  )
  return []
