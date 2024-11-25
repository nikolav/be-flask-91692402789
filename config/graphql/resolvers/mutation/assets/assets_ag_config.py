
from config.graphql.init import mutation

from src.classes import ResponseStatus

from flask_app     import db
from flask_app     import io

from models.assets import Assets
from models.assets import AssetsIOEvents


# assetsAGConfig(ag_config: JsonData!, assets_type: String!): JsonData!
@mutation.field('assetsAGConfig')
def resolve_assetsAGConfig(_obj, _info, ag_config, assets_type):
  # add groups GID:22, GID:333 to Assets:122..
  #   ag_config: { '+122': [22, 333], '-2 +22': [1], etc. }
  r  = ResponseStatus()
  ga = {
    # gid.1: { '+' : set(), '-': set() }
    # gid.2: { '+' : set(), '-': set() }
    #  n...
  }
  changes = 0

  try:
    for aKeys, lsGids in ag_config.items():
      for gid in lsGids:
        for k in aKeys.split(' '):
          aid = int(k[1:])
          ga.setdefault(gid, 
            { '+': set(), '-': set() })[k[0]].add(aid)
    
    for g in Assets.by_ids(*ga.keys()):
      if 0 < len(ga[g.id]['+']):
        changes += g.assets_join(
          *Assets.by_ids_and_type(*[ID for ID in ga[g.id]['+']], 
          type = assets_type))
      
      if 0 < len(ga[g.id]['-']):
        changes += g.assets_leave(
          *Assets.by_ids_and_type(*[ID for ID in ga[g.id]['-']], 
          type = assets_type))
    
    if 0 < changes:
      db.session.commit()
    

  except Exception as err:
    r.error = err


  else:
    r.status = { 'changes': changes }
    if 0 < changes:
      for gid in ga.keys():
        io.emit(f'{AssetsIOEvents.IOEVENT_ASSETS_CONFIGRED_prefix.value}{gid}')

  
  return r.dump()

