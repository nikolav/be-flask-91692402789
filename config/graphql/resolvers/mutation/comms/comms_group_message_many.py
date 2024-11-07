

from config.graphql.init          import mutation
from src.classes                  import ResponseStatus
from schemas.validation.messaging import SchemaChatMessage as SchemaMessageMany

from models.assets import Assets
from models.assets import AssetsType
from models.tags   import Tags
from models.docs   import Docs

from flask_app import TOPIC_CHAT_ASSETS_prefix
from flask_app import IOEVENT_DOCS_CHANGE_JsonData

from flask_app import db
from flask_app import io


# commsGroupMessageMany(gids: [ID!]!, message: JsonData!): JsonData!
@mutation.field('commsGroupMessageMany')
def resolve_commsGroupMessageMany(_obj, _info, gids, message):
  r = ResponseStatus()
  gids_affected = []

  try:
    msg = SchemaMessageMany().load(message)
    for g in Assets.by_ids_and_type(*set(gids), 
                                    type = AssetsType.PEOPLE_GROUP_TEAM.value):
      t = Tags.by_name(f'{TOPIC_CHAT_ASSETS_prefix}{g.id}', 
                       create = True, _commit = False)
      d = Docs(data = msg)
      t.docs.append(d)
      db.session.add(d)
      gids_affected.append(g.id)

    db.session.commit()


  except Exception as err:
    r.error = err
  
  
  else:
    r.status = { 'gids': gids_affected }
    for gid in gids_affected:
      io.emit(f'{IOEVENT_DOCS_CHANGE_JsonData}{TOPIC_CHAT_ASSETS_prefix}{gid}')


  return r.dump()
  
  