from flask      import Blueprint
from flask_cors import CORS

bp_testing = Blueprint('testing', __name__, url_prefix = '/test')

# cors blueprints as wel for cross-domain requests
CORS(bp_testing)


@bp_testing.route('/', methods = ('POST',))
def testing_home():    
  from flask_app import db
  from models.assets import Assets
  from models.users  import Users
  from schemas.serialization import SchemaSerializeAssets
  
  a = db.session.get(Assets, 2)
  return SchemaSerializeAssets(many = True).dump(a.assets_belong)

  # from servcies.firebase.messaging import send as cloud_messaging_send_message
  
  # # get cached tokens for user devices
  # FCM_TOKENS = (
  #   'duxCWVRBOd6TVpTa5Owm-x:APA91bGeavyRk4gYcs--3l9QLz3KwBxFa4CN9oJUS9pUmKHQrqOcqU6E6MOIiMHNMmNg2Oh7T2VjYrmnxiHlJeWtsmUBGz055c0-gwiE7WP1lepIZ2qFkuXfcTlQb2mtSF9hKNiO5m1v',
  #   # 'dBEovId_XfekqVmCtFLe3A:APA91bEXzarogiCzA9NXUkyVMPGOzPOyvE5e9Mj7qTajCb3zFj0zTwMmVz4OTdlB3N4TeIOI-mF1qhe7HHLwVzw83aQ-4eHX4pWlMF4FHeh9K2aRJJ5s1IuTLQNWEnd1eO-QC8kqasKE',
  # )

  # response = cloud_messaging_send_message(
  #   tokens = FCM_TOKENS, 
  #   message_payload = {
  #     'title' : 'title --1',
  #     'body'  : 'body --1',
  #   })
  # return { 'fcm:response': str(response) }
  return []
