
from config.graphql.init import mutation
from flask_app           import db
from models.users        import Users
from models.assets       import Assets
from models.assets       import AssetsType


@mutation.field('groupsGUConfigure')
def resolve_groupsGUConfigure(_obj, _info, guConfig):
  r  = { 'error': None, 'status': None }
  ug = {
    # 1: { 'join' : set(), 'leave': set() }
    # 2: { 'join' : set(), 'leave': set() }
    # etc..
  }
  changes = 0

  try:
    
    for gKeys, lsuids in guConfig.items():
      for uid in lsuids:
        for k in gKeys.split(' '):
          g = int(k[1:])
          ug.setdefault(uid, { 'join': set(), 'leave': set() })['join' if k.startswith('+') else 'leave'].add(g)

    
    for u in Users.by_ids(*ug.keys()):
      
      if 0 < len(ug[u.id]['join']):
        changes += u.assets_join(*Assets.by_ids_and_type(
          *[ID for ID in ug[u.id]['join']], 
          type = AssetsType.PEOPLE_GROUP_TEAM.value))
      
      if 0 < len(ug[u.id]['leave']):
        changes += u.assets_leave(*Assets.by_ids_and_type(
          *[ID for ID in ug[u.id]['leave']], 
          type = AssetsType.PEOPLE_GROUP_TEAM.value))

    
    if 0 < changes:
      db.session.commit()
    

  except Exception as err:
    r['error'] = str(err)


  else:
    r['status'] = { 'changes': changes }

  
  return r

