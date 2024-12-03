
import json
import requests

from flask import g

from config.graphql.init import mutation
from flask_app           import URL_VIBER_MESSAGE_POST
from flask_app           import VIBER_USER_CHANNELS_prefix
from src.classes         import ResponseStatus


@mutation.field('viberSendTextMessage')
def resolve_viberSendTextMessage(_obj, _info, payload):
  r      = ResponseStatus()
  result = []

  try:
    from flask_app import redis_client
    _err, client = redis_client

    for channel_name, text in payload.items():
      key_ = f'{VIBER_USER_CHANNELS_prefix}{g.user.key}:{channel_name}'
      if client.exists(key_):
        ch_info = json.loads(client.get(key_).decode())
        result.append(
          requests.post(URL_VIBER_MESSAGE_POST,
                json = {
                  'auth_token' : ch_info['auth_token'],
                  'from'       : ch_info['from'],
                  'type'       : 'text',
                  'text'       : text
                }).json())


  except Exception as err:
    r.error = err
    

  else:
    r.status = result
    

  return r.dump()

