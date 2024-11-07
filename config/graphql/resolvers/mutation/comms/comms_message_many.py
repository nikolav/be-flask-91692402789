
from flask import g

from marshmallow import fields
from marshmallow import Schema

from config.graphql.init import mutation

from flask_app import db
from flask_app import io
from flask_app import TOPIC_CHAT_USER_CHANNEL_prefix
from flask_app import IOEVENT_DOCS_CHANGE_JsonData

from models.users import Users
from models.docs  import Docs
from models.tags  import Tags

from src.classes import ResponseStatus
from schemas.validation.messaging import SchemaChatMessage as SchemaMessageMany


# commsMessageMany(uids: [ID!]!, message: JsonData!): JsonData!
@mutation.field('commsMessageMany')
def resolve_commsMessageMany(_obj, _info, uids, message):
  
  uids_affected = []
  r = ResponseStatus()

  try:
    
    msg = SchemaMessageMany().load(message)
    for u in Users.by_ids(*set(uids)):
      if g.user.id != u.id:
        t = Tags.by_name(
          f'{TOPIC_CHAT_USER_CHANNEL_prefix}{u.id}', 
          create = True)
        d = Docs(data = msg)
        t.docs.append(d)
        db.session.add(d)
        uids_affected.append(u.id)

    db.session.commit()


  except Exception as err:
    r.error = err


  else:
    r.status = { 'uids': uids_affected }
    for uid_ in uids_affected:
      io.emit(f'{IOEVENT_DOCS_CHANGE_JsonData}{TOPIC_CHAT_USER_CHANNEL_prefix}{uid_}')
  

  return r.dump()

