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
    tokens  = [
      'eZpHzgB-gPkyPmSpSdxbkM:APA91bGP-QPnrgvpAcDmUZpWYuhX3FChOSzcUE07nMofBojroSTiun5aRME4WmHu1-G6LoEuvJ-vyGst95PYwj8Dsa9g5ekkt4yDPKTgKss5xGkUmQ1B8Q6WwZkfQ86IkugK21mriWh3',
      'eZpHzgB-gPkyPmSpSdxbkM:APA91bHwE4oz7X8kNM-9eBXBO4wRTLkvSHSycslfrUsKUQybYgnt3cJMYptNqRgIKoVlPsOT3Bjh8LHGqvpRimex0OgIBeIt7DxDbwVdbRTrwV3fwIScNjv4q2oMjO5kHLqZG8qSZ3b1',
      'eZpHzgB-gPkyPmSpSdxbkM:APA91bGa0BRUUpyvetTB34shGViIqmpxoatN5b_jfSOTJAi8f8n4wGHLkWNj2Kxhtwl2DyZNEN4mVi8jEkGkML6jiAobklPr0L2tvtWNxRLAEPh8aYY2elVN-jRYJ3oW9QR4HiwHZUl-',
    ],
    payload = {'title': 'fcm:demo:3', 'body': str(datetime.now(tz = timezone.utc))}
  )
  return []
