
from config.graphql.init import mutation

from src.classes import ResponseStatus

from flask_app     import db
from flask_app     import io

from models.assets import Assets
from models.assets import AssetsType
from models.assets import AssetsIOEvents


# sitesSGConfig(sgConfig: JsonData!): JsonData!
@mutation.field('sitesSGConfig')
def resolve_sitesSGConfig(_obj, _info, sgConfig):
  # add groups GID:22, GID:333 to SITE:Assets:122..
  #   sgConfig: { '+122': [22, 333], '-2 +22': [1], etc. }
  r  = ResponseStatus()
  gs = {
    # gid.1: { '+' : set(), '-': set() }
    # gid.2: { '+' : set(), '-': set() }
    #  n...
  }
  changes        = 0
  sites_affected = set()

  try:
    for sKeys, lsGids in sgConfig.items():
      for gid in lsGids:
        for k in sKeys.split(' '):
          sid = int(k[1:])
          gs.setdefault(gid, 
            { '+': set(), '-': set() })[k[0]].add(sid)
          sites_affected.add(sid)
    
    for g in Assets.by_ids(*gs.keys()):
      if 0 < len(gs[g.id]['+']):
        changes += g.assets_join(
          *Assets.by_ids_and_type(*[ID for ID in gs[g.id]['+']], 
          type = AssetsType.PHYSICAL_STORE.value))
      
      if 0 < len(gs[g.id]['-']):
        changes += g.assets_leave(
          *Assets.by_ids_and_type(*[ID for ID in gs[g.id]['-']], 
          type = AssetsType.PHYSICAL_STORE.value))
    
    if 0 < changes:
      db.session.commit()
    

  except Exception as err:
    r.error = err


  else:
    r.status = { 'changes': changes }
    if 0 < changes:
      for sid in sites_affected:
        io.emit(f'{AssetsIOEvents.IOEVENT_SITE_GROUPS_CONFIGRED_prefix.value}{sid}')

  
  return r.dump()

