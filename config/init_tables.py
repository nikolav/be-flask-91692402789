
from flask_app    import db

from models.users import Users
from models.tags  import Tags
from models.docs  import Docs
from .            import init_docs_tags
from utils.pw     import hash as hashPassword

from flask_app import ADMIN_EMAIL
from flask_app import ADMIN_PASSWORD
from flask_app import APP_NAME
from flask_app import POLICY_ADMINS
from flask_app import POLICY_ALL
from flask_app import POLICY_APPROVED
from flask_app import POLICY_EMAIL
from flask_app import POLICY_FILESTORAGE
from flask_app import POLICY_MANAGERS
from flask_app import TAG_ARCHIVED
from flask_app import TAG_EMAIL_VERIFIED
from flask_app import TAG_USERS_EXTERNAL
from flask_app import TAG_VARS
from flask_app import USER_EMAIL
from flask_app import USER_PASSWORD


# --admin
email_    = ADMIN_EMAIL
password_ = ADMIN_PASSWORD
# --user
emailUser_    = USER_EMAIL
passwordUser_ = USER_PASSWORD

user_admin   = db.session.scalar(db.select(Users).where(Users.email == email_))
user_default = db.session.scalar(db.select(Users).where(Users.email == emailUser_))

if not user_admin:
  user_admin = Users(email = email_, password = hashPassword(password_))
  db.session.add(user_admin)

if not user_default:
  user_default = Users(email = emailUser_, password = hashPassword(passwordUser_))
  db.session.add(user_default)

db.session.commit()


for t in init_docs_tags:
  Tags.by_name(t, create = True)

tag_vars = Tags.by_name(TAG_VARS)

vars_data = [doc.data for doc in tag_vars.docs]

if all(not 'app:name' in node for node in vars_data):
  tag_vars.docs.append(Docs(data = {'app:name': APP_NAME }))

if all(not 'admin:email' in node for node in vars_data):
  tag_vars.docs.append(Docs(data = {'admin:email': email_ }))
  
db.session.commit()


# default tags
policy_fs_       = POLICY_FILESTORAGE
policy_approved_ = POLICY_APPROVED
policy_email_    = POLICY_EMAIL
policy_admins_   = POLICY_ADMINS
policy_managers_ = POLICY_MANAGERS
policy_all_      = POLICY_ALL

# init
tagPolicyADMINS          = Tags.by_name(policy_admins_,                  create = True)
tagPolicyMANAGERS        = Tags.by_name(policy_managers_,                create = True)
tagPolicyEMAIL           = Tags.by_name(policy_email_,                   create = True)
tagPolicyFS              = Tags.by_name(policy_fs_,                      create = True)
tagPolicy_approved       = Tags.by_name(policy_approved_,                create = True)
tagPolicyALL             = Tags.by_name(policy_all_,                     create = True)
tag_archived             = Tags.by_name(TAG_ARCHIVED,                    create = True)
tag_email_verified       = Tags.by_name(TAG_EMAIL_VERIFIED,              create = True)
tag_users_external       = Tags.by_name(TAG_USERS_EXTERNAL,              create = True)

# users:policies --default
user_admin.policies_add(
  policy_approved_,
  policy_admins_,
  policy_email_,
  policy_fs_
  # policy_managers_,
  # policy_all_,
)

# user_default.policies_add(
#   policy_approved_,
#   policy_email_,
#   policy_fs_
# )

db.session.commit()


d_vibchannels = Docs.viber_channels()
if 0 == len(d_vibchannels.data):
  from config.vars import viber_channels
  d_vibchannels.data = viber_channels.copy()
  db.session.commit()

