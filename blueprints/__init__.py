import sqlalchemy

from flask      import Blueprint
from flask_cors import CORS

from config         import TAG_VARS
from models.docs    import Docs
from models.tags    import Tags
from models.users   import Users
from utils.jwtToken import encode
from flask_app      import db
from flask_app      import ADMIN_EMAIL
from flask_app      import USER_EMAIL
from flask_app      import POLICY_ADMINS


bp_home = Blueprint('home', __name__, url_prefix = '/')

# cors blueprints as wel for cross-domain requests
CORS(bp_home)

@bp_home.route('/', methods = ('GET',))
def status_ok():
  
  admin_email = ''
  app_name    = ''
  
  
  for d in Docs.tagged(TAG_VARS):

    if 'app:name' in d.data:
      app_name = d.data['app:name']
      
    if 'admin:email' in d.data:
      admin_email = d.data['admin:email']
    
    if app_name and admin_email:
      break

  
  uid_admin = db.session.scalar(
    db.select(Users.id)
    .where(Users.email == ADMIN_EMAIL)
  )
  
  uid = db.session.scalar(
    db.select(Users.id)
    .where(Users.email == USER_EMAIL)
  )
  
  
  uids_admin = [u.id for u in Tags.by_name(POLICY_ADMINS).users]

  
  redis_client_version = None
  try:
    from flask_app import redis_client
    _err, redis_cli = redis_client
    redis_client_version = redis_cli.info().get('redis_version')
  except:
    pass

  return {
    'status'        : 'ok',
    'app:name'      : app_name,
    'admin:email'   : admin_email,
    'admin:uid'     : uid_admin,
    'default:uid'   : uid,
    'token:default' : encode({ 'id': uid }),
    'admins'        : uids_admin,
    'sqlalchemy'    : sqlalchemy.__version__,
    'redis'         : redis_client_version,
  }

