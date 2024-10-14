from flask      import Blueprint
from flask_cors import CORS

bp_testing = Blueprint('testing', __name__, url_prefix = '/test')

# cors blueprints as wel for cross-domain requests
CORS(bp_testing)


@bp_testing.route('/', methods = ('POST',))
def testing_home():     
  from models.assets import Assets
  from flask_app import db
  from schemas.serialization import SchemaSerializeAssets
  a = db.session.get(Assets, 1)
  # a2 = db.session.get(Assets, 15)
  ls = Assets.assets_parents(a, TYPE = 'DIGITAL_FORM:TzZJs5PZqcWc')
  return SchemaSerializeAssets(many = True, exclude = ('assets_has',)).dump(ls)
  # from flask import g
  # from servcies.firebase.messaging import send
  # from datetime import datetime
  # from datetime import timezone
  # send(
  #   tokens  = [
  #     'tok1',
  #     'tok2',
  #   ],
  #   payload = {'title': 'fcm:demo:3', 'body': str(datetime.now(tz = timezone.utc))}
  # )
  return []
