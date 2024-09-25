from flask      import Blueprint
from flask_cors import CORS

from flask import request
from flask import make_response
from flask import jsonify

from flask_app import db
from models.docs import Docs
from models.tags import Tags


bp_webhook_viber_channel = Blueprint('webhook_viber_channel', __name__, url_prefix = '/webhook_viber_channel')

# cors blueprints as wel for cross-domain requests
CORS(bp_webhook_viber_channel)


@bp_webhook_viber_channel.route('/<string:webhook_name>', methods = ('POST',))
def route_handle_webhook(webhook_name = ""):
  data = request.get_json()
  
  t_wh = Tags.by_name(f'webhook:{webhook_name}', create = True)
  d = Docs(data = data)
  t_wh.docs.append(d)

  db.session.add(t_wh)
  db.session.commit()

  return make_response(jsonify(None), 200)

