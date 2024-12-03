from flask       import Blueprint
from flask_cors  import CORS

from src.classes import ResponseStatus

TAG_WEBHOOK_VIBER = 'WEBHOOK_VIBER:0NUXeH5Xi1eofFYZIVug:'

bp_testing = Blueprint('testing', __name__, url_prefix = '/test')


# cors blueprints as wel for cross-domain requests
CORS(bp_testing)

@bp_testing.route('/', methods = ('POST',))
def testing_home():  
  from flask import request
  from flask_app import redis_client
  from datetime import datetime
  from datetime import timezone
  _err, client = redis_client

  # wh:01

  whname = request.get_json().get('webhook_name')

  r = ResponseStatus()
  
  res = client.set(f'{TAG_WEBHOOK_VIBER}{whname}', datetime.now(tz = timezone.utc).isoformat())
  # res = client.get(f'{TAG_WEBHOOK_VIBER}{whname}').decode()
  r.status = str(res)


  return r.dump()

