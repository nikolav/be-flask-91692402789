
from config.graphql.init import mutation
from src.classes         import ResponseStatus
from flask_app           import db
from models.assets       import Assets
from models.assets       import AssetsIOEvents
from flask_app           import io


# assetsManageTags(aid: ID!, config: JsonData!): JsonData!
@mutation.field('assetsManageTags')
def resolve_assetsManageTags(_obj, _info, aid, config):
  # config: { <string:tag-name>: boolean:add-remove-flag }
  changes = 0
  r = ResponseStatus()
  a = None

  try:
    if config:
      a = db.session.get(Assets, aid)
      if not a:
        raise Exception(f'asset:#{aid}:not-found')
      
      tls_add = (t for t, flag in config.items() if True  == flag)
      tls_rm  = (t for t, flag in config.items() if False == flag)

      changes += a.tags_add(*tls_add, _commit = False)
      changes += a.tags_rm(*tls_rm,   _commit = False)

      if 0 < changes:
        db.session.commit()


  except Exception as err:
    r.error = err

  else:
    r.status = { 'changes': changes }
    if 0 < changes:
      io.emit(f'{AssetsIOEvents.IOEVENT_ASSETS_CONFIGRED_prefix.value}{a.id}')


  return r.dump()



  