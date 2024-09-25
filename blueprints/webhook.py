from flask      import Blueprint
from flask_cors import CORS

bp_webhook = Blueprint('webhook', __name__, url_prefix = '/webhook')

# cors blueprints as wel for cross-domain requests
CORS(bp_webhook)


@bp_webhook.route('/<string:name>', methods = ('POST',))
def route_handle_webhook(name = ""):
  from flask import request
  from flask import make_response
  from flask import jsonify

  from flask_app import db
  from models.docs import Docs
  from models.tags import Tags

  data = request.get_json()
  
  t_wh = Tags.by_name(f'webhook:{name}', create = True)
  d = Docs(data = data)
  t_wh.docs.append(d)

  db.session.add(t_wh)
  db.session.commit()

  return make_response(jsonify(None), 200)

