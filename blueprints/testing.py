from flask      import Blueprint
from flask_cors import CORS

bp_testing = Blueprint('testing', __name__, url_prefix = '/test')

# cors blueprints as wel for cross-domain requests
CORS(bp_testing)


@bp_testing.route('/', methods = ('POST',))
def testing_home():     
  from flask_app import db
  from models.users import Users
  from schemas.serialization import SchemaSerializeUsersTimes
  u2 = db.session.get(Users, 2)
  return SchemaSerializeUsersTimes(many = True).dump(u2.users_followers)
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
