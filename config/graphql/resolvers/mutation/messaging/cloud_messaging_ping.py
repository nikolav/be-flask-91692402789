from flask       import g
from marshmallow import EXCLUDE

from flask_app                    import KEY_FCM_DEVICE_TOKENS
from models.docs                  import Docs
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
    
    d_tokens        = Docs.by_doc_id(f'{KEY_FCM_DEVICE_TOKENS}{g.user.id}')
    ls_tokens_valid = tuple(t_key for t_key, t_val in d_tokens.data.items() if True == t_val)

    if 0 < len(ls_tokens_valid):
      res = send(
        tokens  = ls_tokens_valid,
        payload = message_validated
      )
      r['status'] = str(res)

  except Exception as err:
    r['error'] = str(err)

  return r

