from flask      import Blueprint
from flask_cors import CORS

bp_testing = Blueprint('testing', __name__, url_prefix = '/test')

# cors blueprints as wel for cross-domain requests
CORS(bp_testing)


@bp_testing.route('/', methods = ('POST',))
def testing_home():  
  from servcies.firebase.messaging import send as cloud_messaging_send_message
  
  # get cached tokens for user devices
  FCM_TOKENS = (
    'duxCWVRBOd6TVpTa5Owm-x:APA91bGeavyRk4gYcs--3l9QLz3KwBxFa4CN9oJUS9pUmKHQrqOcqU6E6MOIiMHNMmNg2Oh7T2VjYrmnxiHlJeWtsmUBGz055c0-gwiE7WP1lepIZ2qFkuXfcTlQb2mtSF9hKNiO5m1v',
  )

  response = cloud_messaging_send_message(
    tokens = FCM_TOKENS, 
    message_payload = {
      'title' : 'title --1',
      'body'  : 'body --1',
    })
  return { 'fcm:response': str(response) }
