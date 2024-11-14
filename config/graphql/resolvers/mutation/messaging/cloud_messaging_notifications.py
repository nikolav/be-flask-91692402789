
from config.graphql.init import mutation

from schemas.validation.messaging import SchemaValidateNotificationMessage
from servcies.firebase.messaging  import notification_send

from models.users import Users

from src.classes import ResponseStatus


# cloudMessagingNotifications(uids: [ID!]!, payload: JsonData!):JsonData!
@mutation.field('cloudMessagingNotifications')
def resolve_cloudMessagingNotifications(_obj, _info, uids, payload):
  r         = ResponseStatus()
  responses = []

  try:
    p = SchemaValidateNotificationMessage().load(payload)
    payload_ = { 
      'title': p['title'], 
      'body' : p['body']
    }
    image_ = p.get('image')
    tokens = set()
    
    for u in Users.by_ids(*uids):
      tokens.update(u.cloud_messaging_device_tokens())
    
    if 0 < len(tokens):
      responses.append(
        notification_send(
          tokens  = list(tokens),
          payload = payload_,
          image   = image_
        ))


  except Exception as err:
    r.error = err


  else:
    r.status = { 'responses': [str(res) for res in responses] }


  return r.dump()

