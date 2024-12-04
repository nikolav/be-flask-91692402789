
from datetime import datetime
from datetime import timezone

import requests

from config.graphql.init import mutation
from src.classes         import ResponseStatus

from flask_app import URL_VIBER_SET_WEBHOOK
from flask_app import VIBER_URL_ACCOUNT_INFO

from flask     import g
from flask_app import db


# viberChannelSetupSetWebhook(url: String!, auth_token: String!, is_global: Boolean): JsonData!
@mutation.field('viberChannelSetupSetWebhook')
def resolve_viberChannelSetupSetWebhook(_obj, _info, url, auth_token, is_global = False):
  r = ResponseStatus()
  
  ch_name = None
  ch_info = None

  try:
    
    # validate url
    dp = requests.post(URL_VIBER_SET_WEBHOOK, 
                    json = {
                      'url'        : url,
                      'auth_token' : auth_token,
                    }).json()
    if dp.get('status'):
      raise Exception('viber:setup:error')
    
    # access viber account
    di = requests.post(VIBER_URL_ACCOUNT_INFO,
                      json = {
                        'auth_token': auth_token,
                      }).json()
    if di.get('status'):
      raise Exception('viber:setup:error')
    
    # cache channel admin account info for sending messages
    ch_admin = next((m for m in di['members'] if 'superadmin' == m['role']), None)
    if not ch_admin:
      raise Exception('viber:setup:error:no-channel-admin')
    
    ch_name = di['name']
    ch_info = { 
                'from'       : ch_admin['id'], 
                'auth_token' : auth_token, 
                'is_global'  : is_global,
              }

    g.user.profile_update(
      patch = {
        'viber_channels': {
          ch_name: datetime.now(tz = timezone.utc).isoformat()
        }
      })
    db.session.commit()


  except Exception as err:
    r.error = err

  
  else:
    r.status = { 'channel': { 'name': ch_name, 'info': ch_info } }


  return r.dump()
  

