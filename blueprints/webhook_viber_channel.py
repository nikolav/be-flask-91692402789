
from flask      import Blueprint
from flask_cors import CORS

from flask import make_response
from flask import jsonify


bp_webhook_viber_channel = Blueprint('webhook_viber_channel', __name__, url_prefix = '/webhook_viber_channel')

# cors blueprints
CORS(bp_webhook_viber_channel)

@bp_webhook_viber_channel.route('/<string:webhook_name>', methods = ('POST',))
def route_handle_webhook_viber_channel(webhook_name = ''):
  # webhook_name:string <user_key>:<channel_name>
  # data { 
  #  "event":"webhook", 
  #  "timestamp":1457764197627, 
  #  "message_token":241256543215 
  #  "chat_hostname": "tN6Hzq",
  # }   
  return make_response(jsonify(None), 200)

