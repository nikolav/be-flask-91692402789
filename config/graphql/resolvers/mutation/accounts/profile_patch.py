
from copy import deepcopy

from flask import g

from config.graphql.init    import mutation
from flask_app              import db
from models.users           import Users
from utils.merge_strategies import dict_deepmerger_extend_lists as merger
from flask_app              import IOEVENT_ACCOUNTS_UPDATED_prefix
from flask_app              import io


@mutation.field('accountsProfilePatch')
def resolve_accountsProfilePatch(_obj, _inf, uid, patch):
  # accountsProfilePatch(uid: ID!, patch: JsonData!): JsonData!
  r           = { 'error': None, 'status': None }
  profile_new = None
  id          = None
  
  try:
    u = db.session.get(Users, uid)
    # if account exists
    if u:
      if not g.user.can_manage_account(u.id):
        raise Exception('accountsProfilePatch --access-denied')
      
      profile_new = merger.merge(deepcopy(u.profile), patch)
      u.profile = profile_new
      db.session.commit()

      # account row-id affected
      id = u.id


  except Exception as err:
    r['error'] = str(err)

  
  else:
    r['status'] = { 'profile': profile_new }
    if id:
      io.emit(f'{IOEVENT_ACCOUNTS_UPDATED_prefix}{id}')
    

  return r

