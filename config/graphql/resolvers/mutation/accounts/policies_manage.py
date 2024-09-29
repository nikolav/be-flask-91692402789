
from config.graphql.init  import mutation
from models.users         import Users
from middleware.authguard import authguard

from flask_app  import POLICY_ADMINS
from flask_app  import POLICY_MANAGERS
from flask_app  import TAG_ARCHIVED
from flask_app  import POLICY_APPROVED
from flask_app  import POLICY_EMAIL
from flask_app  import POLICY_FILESTORAGE
from flask_app  import TAG_EMAIL_VERIFIED
from flask_app  import TAG_USERS_EXTERNAL

from utils import Lists

from flask_app import io
from flask_app import IOEVENT_ACCOUNTS_UPDATED


POLICIES_CONFIGURABLE = {
  'admins'         : POLICY_ADMINS,
  'approved'       : POLICY_APPROVED,
  'archived'       : TAG_ARCHIVED,
  'email_verified' : TAG_EMAIL_VERIFIED,
  'email'          : POLICY_EMAIL,
  'external'       : TAG_USERS_EXTERNAL,
  'managers'       : POLICY_MANAGERS,
  'storage'        : POLICY_FILESTORAGE,
}


@mutation.field('accountsPoliciesManage')
@authguard(POLICY_ADMINS)
def resolve_accountsPoliciesManage(_obj, _inf, policies):
  # accountsPoliciesManage(policies: JsonData!): JsonData!
  # policies: { [uid: ID]: { [policy: string]: flag:boolean } }
  r           = { 'error': None, 'status': None }
  num_changes = 0
  
  try:
    ls_u = Users.by_uids(*policies.keys())
    for u in ls_u:
      p = policies[str(u.id)]
      keys_configurable = Lists.intersection(p.keys(), POLICIES_CONFIGURABLE.keys())
      num_changes += u.policies_patch(
        { POLICIES_CONFIGURABLE[pname]: p[pname] for pname in keys_configurable})

  except Exception as err:
    r['error'] = str(err)
  
  else:
    r['status'] = { 'changes': num_changes }
    if 0 < num_changes:
      io.emit(IOEVENT_ACCOUNTS_UPDATED)

  return r

