from flask       import g
from marshmallow import EXCLUDE

from config.graphql.init          import mutation
from schemas.validation.messaging import SchemaValidateMessage
# from servcies.firebase.messaging  import message_silent_send
from servcies.firebase.messaging  import notification_send


@mutation.field('cloudMessagingPing')
def resolve_cloudMessagingPing(_obj, _info, 
                               payload = {
                                 'title' : 'message --PING', 
                                 'body'  : 'body --PING'
                                }):
  r   = { 'error': None, 'status': None }
  res = None

  try:

    # res = message_silent_send(
    res = notification_send(
      tokens  = g.user.cloud_messaging_device_tokens(),
      payload = SchemaValidateMessage(unknown = EXCLUDE).load(payload)
    )
    

  except Exception as err:
    r['error'] = str(err)

  
  else:
    r['status'] = str(res)


  return r

