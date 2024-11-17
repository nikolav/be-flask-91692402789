
from config.graphql.init import mutation

from src.classes import ResponseStatus

from flask_app     import db
from flask_app     import io

from models.assets import Assets
from models.assets import AssetsType
from models.assets import AssetsIOEvents


# channelsCGConfig(cgConfig: JsonData!): JsonData!
@mutation.field('channelsCGConfig')
def resolve_sitesSGConfig(_obj, _info, cgConfig):
  # add groups GID:22, GID:333 to CHANNEL:Assets:122..
  #   cgConfig: { '+122': [22, 333], '-2 +22': [1], etc. }
  r  = ResponseStatus()
  gc = {
    # gid.1: { '+' : set(), '-': set() }
    # gid.2: { '+' : set(), '-': set() }
    #  n...
  }
  changes = 0
  # channels_affected = set()

  try:
    for cKeys, lsGids in cgConfig.items():
      for gid in lsGids:
        for k in cKeys.split(' '):
          cid = int(k[1:])
          gc.setdefault(gid, 
            { '+': set(), '-': set() })[k[0]].add(cid)
          # channels_affected.add(cid)
    
    for g in Assets.by_ids(*gc.keys()):
      if 0 < len(gc[g.id]['+']):
        changes += g.assets_join(
          *Assets.by_ids_and_type(*[ID for ID in gc[g.id]['+']], 
          type = AssetsType.DIGITAL_CHAT.value))
      
      if 0 < len(gc[g.id]['-']):
        changes += g.assets_leave(
          *Assets.by_ids_and_type(*[ID for ID in gc[g.id]['-']], 
          type = AssetsType.DIGITAL_CHAT.value))
    
    if 0 < changes:
      db.session.commit()
    

  except Exception as err:
    r.error = err


  else:
    r.status = { 'changes': changes }
    if 0 < changes:
      for gid in gc.keys():
        io.emit(f'{AssetsIOEvents.IOEVENT_ASSETS_CONFIGRED_prefix.value}{gid}')

  
  return r.dump()

