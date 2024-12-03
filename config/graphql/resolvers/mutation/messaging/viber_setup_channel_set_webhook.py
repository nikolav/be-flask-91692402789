
import requests
import json

from flask import g

from config.graphql.init import mutation
from src.classes         import ResponseStatus

from flask_app import VIBER_USER_CHANNELS_prefix


URL_VIBER_SET_WEBHOOK  = 'https://chatapi.viber.com/pa/set_webhook'
VIBER_URL_ACCOUNT_INFO = 'https://chatapi.viber.com/pa/get_account_info'

# viberChannelSetupSetWebhook(url: String!, auth_token: String!): JsonData!
@mutation.field('viberChannelSetupSetWebhook')
def resolve_viberChannelSetupSetWebhook(_obj, _info, url, auth_token):
  r = ResponseStatus()

  try:
    from flask_app import redis_client
    _err, client = redis_client
    
    dp = requests.post(URL_VIBER_SET_WEBHOOK, 
                    json = {
                      'url'        : url,
                      'auth_token' : auth_token,
                    }).json()
    if 0 != dp.get('status') or 'ok' != dp.get('status_message'):
      raise Exception('viber:setup:error')
    
    di = requests.post(VIBER_URL_ACCOUNT_INFO,
                      json = {
                        'auth_token': auth_token,
                      }).json()
    if 0 != di.get('status') or 'ok' != di.get('status_message'):
      raise Exception('viber:setup:error')
    
    u = next((m for m in di['members'] if 'superadmin' == m['role']), None)
    if not u:
      raise Exception('viber:setup:error:no-role-sa')
    
    ch_name = di['name']
    dd      = { 'from': u.id, 'auth_token': auth_token }
    
    KEY_user_channel = f'{g.user.key}:{ch_name}'
    client.set(f'{VIBER_USER_CHANNELS_prefix}{KEY_user_channel}', json.dumps(dd))


  except Exception as err:
    r.error = err

  
  else:
    r.status = { 'channel': { ch_name: dd } }


  return r.dump()
  

