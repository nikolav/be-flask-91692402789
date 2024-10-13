from flask      import Blueprint
from flask_cors import CORS

bp_testing = Blueprint('testing', __name__, url_prefix = '/test')

# cors blueprints as wel for cross-domain requests
CORS(bp_testing)


@bp_testing.route('/', methods = ('POST',))
def testing_home():     
  from schemas.validation.acconts import SchemaAccountsAddCredentialsPayload
  p = SchemaAccountsAddCredentialsPayload(partial = ('policies',)).load({'email': 'foo@foo.com', 'password': 'foo', 'policies': ['admin', 'external']})
  return {'p': [e.value for e in p.get('policies', [])]}
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
