from flask      import Blueprint
from flask_cors import CORS

bp_testing = Blueprint('testing', __name__, url_prefix = '/test')

# cors blueprints as wel for cross-domain requests
CORS(bp_testing)


@bp_testing.route('/', methods = ('POST',))
def testing_home():     
  r = { 'error': None, 'status': None }

  from flask_app import redis_client

  _err, client = redis_client

  val = client.get("FOO")
  r['status']= { 'result': val.decode() }

  
  return r
