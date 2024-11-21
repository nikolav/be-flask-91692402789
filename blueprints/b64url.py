
import io
import requests
import base64

from flask       import Blueprint
from flask_cors  import CORS

from flask  import request
from flask  import make_response

from marshmallow import Schema
from marshmallow import fields


class SchemaHasUrl(Schema):
  url = fields.URL(required = True)

bp_b64url = Blueprint('b64url', __name__, url_prefix = '/b64url')

# cors blueprints as wel for cross-domain requests
CORS(bp_b64url)

@bp_b64url.route('/', methods = ('POST',))
def route_fn_b64url():

  try:
    d = SchemaHasUrl().load(request.get_json())

    response = requests.get(d['url'])
    if not response.ok:
      raise Exception('--requests:fetch:failed')

    file  = io.BytesIO(response.content)
    fdata = base64.b64encode(file.getvalue()).decode()

    res = make_response(fdata)
    res.headers['Content-Type']   = 'text/plain'
    res.headers['Content-Length'] = len(fdata)

    r = res


  except Exception as err:
    r = f'--error {err}'
  

  return r

