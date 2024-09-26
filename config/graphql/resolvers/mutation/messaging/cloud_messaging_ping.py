from flask       import g
from marshmallow import EXCLUDE

from config.graphql.init          import mutation
from schemas.validation.messaging import SchemaValidateMessage
from servcies.firebase.messaging  import send


@mutation.field('cloudMessagingPing')
def resolve_cloudMessagingPing(_obj, _info, 
                               payload = {
                                 'title' : 'message --ping', 
                                 'body'  : 'body --ping'
                                }):
  r = { 'error': None, 'status': None }

  try:
    message_validated = SchemaValidateMessage(unknown = EXCLUDE).load(payload)
    # message format ok
    res = send(
      tokens  = g.user.cloud_messaging_device_tokens(),
      payload = message_validated
    )
    r['status'] = str(res)

  except Exception as err:
    r['error'] = str(err)

  return r

