import requests

from config.graphql.init import mutation
from models.docs         import Docs
from flask_app           import URL_VIBER_MESSAGE_POST


@mutation.field('viberSendTextMessage')
def resolve_viberSendTextMessage(_obj, _info, payload):
  r = { 'error': None, 'status': None }
  result = None

  try:
    vib_channels = Docs.viber_channels().data
    result = [requests.post(URL_VIBER_MESSAGE_POST,
                json = {
                  'auth_token' : vib_channels[channel_name]['auth_token'],
                  'from'       : vib_channels[channel_name]['from'],
                  'type'       : 'text',
                  'text'       : text
                }).json() 
                  for channel_name, text in payload.items() 
                    if channel_name in vib_channels]
  
  except Exception as err:
    r['error'] = str(err)
    
  else:
    r['status'] = result
    
  return r

