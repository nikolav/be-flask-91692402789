
from flask import g

from config.graphql.init import mutation

from schemas.validation.messaging import SchemaValidateNotificationMessage
from servcies.firebase.messaging  import notification_send

from models.assets import Assets
from models.assets import AssetsType

from src.classes import ResponseStatus
from functools   import reduce


# cloudMessagingNotificationsChats(cids: [ID!]!, payload: JsonData!, AND_THIS: Boolean): JsonData!
@mutation.field('cloudMessagingNotificationsChats')
def resolve_cloudMessagingNotificationsChats(_obj, _info, cids, payload, AND_THIS = True):
  '''
    notify users at channel's:cids related groups
  '''
  r             = ResponseStatus()
  responses     = []
  success_count = 0

  try:
    p = SchemaValidateNotificationMessage().load(payload)
    payload_ = { 
      'title': p['title'], 
      'body' : p['body']
    }
    image_ = p.get('image')
    tokens = set()

    groups = Assets.assets_children(
      *Assets.by_ids_and_type(*cids, 
        type = AssetsType.DIGITAL_CHAT.value))
    
    uid_this = g.user.id
    for g_ in groups:
      for u in g_.users:
        if uid_this == u.id:
          if not AND_THIS:
            continue
        tokens.update(u.cloud_messaging_device_tokens())


    if 0 < len(tokens):
      
      responses.append(
        notification_send(
          tokens  = list(tokens),
          payload = payload_,
          image   = image_
        ))
      
      success_count = reduce(
        lambda c, r: c + r.success_count, responses, 0)
    

  except Exception as err:
    r.error = err


  else:
    r.status = { 'success_count': success_count }


  return r.dump()

