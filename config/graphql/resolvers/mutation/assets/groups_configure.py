
from config.graphql.init import mutation
from flask_app           import db
from flask_app           import io
from models.users        import Users
from models.assets       import Assets
from models.assets       import AssetsType
from models.assets       import AssetsIOEvents

from src.classes import ResponseStatus


@mutation.field('groupsGUConfigure')
def resolve_groupsGUConfigure(_obj, _info, guConfig):
  r  = ResponseStatus()
  ug = {
    # 1: { '+' : set(), '-': set() }
    # 2: { '+' : set(), '-': set() }
    #  etc.
  }
  changes         = 0
  groups_affected = set()

  try:
    for gKeys, lsuids in guConfig.items():
      for uid in lsuids:
        for k in gKeys.split(' '):
          gid = int(k[1:])
          ug.setdefault(uid, 
            { '+': set(), '-': set() })[k[0]].add(gid)
          groups_affected.add(gid)
    
    for u in Users.by_ids(*ug.keys()):
      
      if 0 < len(ug[u.id]['+']):
        changes += u.assets_join(
          *Assets.by_ids_and_type(*[ID for ID in ug[u.id]['+']], 
          type = AssetsType.PEOPLE_GROUP_TEAM.value))
      
      if 0 < len(ug[u.id]['-']):
        changes += u.assets_leave(
          *Assets.by_ids_and_type(*[ID for ID in ug[u.id]['-']], 
          type = AssetsType.PEOPLE_GROUP_TEAM.value))
    
    if 0 < changes:
      db.session.commit()
    

  except Exception as err:
    r.error = err


  else:
    r.status = { 'changes': changes }
    if 0 < changes:
      for gid in groups_affected:
        io.emit(f'{AssetsIOEvents.IOEVENT_PEOPLE_GROUP_TEAM_CONFIGURED_prefix.value}{gid}')

  
  return r.dump()

