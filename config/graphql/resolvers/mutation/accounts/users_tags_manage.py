
from functools import reduce

from flask_app import db
from flask_app import io
from flask_app import USERS_TAGS_prefix
from flask_app import IOEVENT_ACCOUNTS_UPDATED_prefix
from flask_app import IOEVENT_ACCOUNTS_UPDATED

from models.users import Users
from config.graphql.init import mutation


def digits_(ls):
  return filter(lambda node: str(node).isdigit(), ls)

# usersTagsManage(tags: JsonData!): JsonData!
@mutation.field('usersTagsManage')
def resolve_usersTagsManage(_obj, _info, tags):
  # tags { [uid:string]: { [tag:string]: active:boolean } }
  r =  { 'error': None, 'status': None }
  
  changes     = {}
  num_changes = 0

  # for each user
  #  filter valid keys
  #   assign tags; count changes
  
  # build valid tag:value map
  def reducer_tags_manage_(res, field):
    item = res[0]
    t    = res[1]

    if field.startswith(USERS_TAGS_prefix) and isinstance(item[field], bool):
      t['add' if item[field] else 'remove'].add(field)
    
    return res

  
  try:
    for u in Users.by_ids(*digits_(tags.keys())):
      uid          = str(u.id)
      changes[uid] = 0
      
      _0, tags_manage = reduce(reducer_tags_manage_, 
                           tags[uid], 
                           (tags[uid], { 'add': set(), 'remove': set() }))
      changes[uid] += u.policies_add(*tags_manage['add']   , _commit = False)
      changes[uid] += u.policies_rm( *tags_manage['remove'], _commit = False)

      num_changes += changes[uid]
    
    db.session.commit()

    
  except Exception as err:
    r['error'] = str(err)


  else:
    r['status'] = { 'num_changes': num_changes, 'changes': changes }

    # emit updates @user
    for uid, n in changes.items():
      if 0 < n:
        io.emit(f'{IOEVENT_ACCOUNTS_UPDATED_prefix}{uid}')
    if 0 < num_changes:
      io.emit(IOEVENT_ACCOUNTS_UPDATED)
  

  return r

