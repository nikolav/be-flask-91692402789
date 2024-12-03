
import json
import requests

from config.graphql.init import mutation
from src.classes         import ResponseStatus
from flask_app           import URL_VIBER_MESSAGE_POST
from flask_app           import VIBER_CHANNELS_CACHEID
from flask_app           import redis_client


@mutation.field('viberSendTextMessage')
def resolve_viberSendTextMessage(_obj, _info, payload):
  r = ResponseStatus()
  
  result   = []
  channels = {}

  try:
    _err, client = redis_client

    # load viber channels
    if not client.exists(VIBER_CHANNELS_CACHEID):
      client.set(VIBER_CHANNELS_CACHEID, json.dumps(channels))
    else:
      channels = json.loads(client.get(VIBER_CHANNELS_CACHEID).decode())
    
    result = [requests.post(URL_VIBER_MESSAGE_POST,
                json = {
                  'auth_token' : channels[channel_name]['auth_token'],
                  'from'       : channels[channel_name]['from'],
                  'type'       : 'text',
                  'text'       : text
                }).json() 
                  for channel_name, text in payload.items()
                    if channel_name in channels]


  except Exception as err:
    r.error = err
    

  else:
    r.status = result
    

  return r.dump()

