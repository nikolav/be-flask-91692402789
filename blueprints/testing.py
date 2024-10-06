from flask      import Blueprint
from flask_cors import CORS

bp_testing = Blueprint('testing', __name__, url_prefix = '/test')

# cors blueprints as wel for cross-domain requests
CORS(bp_testing)


@bp_testing.route('/', methods = ('POST',))
def testing_home(): 
  from flask_app import db
  from models.users import Users
  from models.users import UsersTagsStatus
  u = db.session.get(Users, 1)
  u.availability_commit(UsersTagsStatus.AWAY.value)
  return { 'id': u.id }

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
