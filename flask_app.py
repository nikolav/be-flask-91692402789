import os

from dotenv           import load_dotenv
from flask            import Flask
from flask_cors       import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_talisman   import Talisman

# https://github.com/miguelgrinberg/flask-socketio/issues/40#issuecomment-48268526
from flask_socketio import SocketIO

# https://pythonhosted.org/Flask-Mail/
from flask_mail import Mail

from flask_pymongo import PyMongo


from src.classes import Base as DbModelBaseClass



FLASKAPP_PATH = os.path.dirname(__file__)

# env:init
load_dotenv()

ENV        = os.getenv('ENV')
PRODUCTION = 'production' == ENV

# app
APP_NAME                       = os.getenv('APP_NAME')
APP_DOMAIN                     = os.getenv('APP_DOMAIN')
ADMIN_EMAIL                    = os.getenv('ADMIN_EMAIL')
ADMIN_PASSWORD                 = os.getenv('ADMIN_PASSWORD')
APP_SECRET_KEY                 = os.getenv('SECRET_KEY')
USER_EMAIL                     = os.getenv('USER_EMAIL')
USER_PASSWORD                  = os.getenv('USER_PASSWORD')
DEFAULT_USER_ID                = os.getenv('DEFAULT_USER_ID')
MAX_BODY_SIZE_MB               = int(os.getenv('MAX_BODY_SIZE_MB'))

# policies
POLICY_ADMINS                  = os.getenv('POLICY_ADMINS')
POLICY_APPROVED                = os.getenv('POLICY_APPROVED')
POLICY_EMAIL                   = os.getenv('POLICY_EMAIL')
POLICY_FILESTORAGE             = os.getenv('POLICY_FILESTORAGE')
POLICY_MANAGERS                = os.getenv('POLICY_MANAGERS')
POLICY_ALL                     = os.getenv('POLICY_ALL')

# db
DATABASE_URI                   = os.getenv('DATABASE_URI_production') if PRODUCTION else os.getenv('DATABASE_URI_dev')
REBUILD_SCHEMA                 = bool(os.getenv('REBUILD_SCHEMA'))
# db records/tags
TAG_ARCHIVED                   = os.getenv('TAG_ARCHIVED')
TAG_EMAIL_VERIFIED             = os.getenv('TAG_EMAIL_VERIFIED')
TAG_USERS_EXTERNAL             = os.getenv('TAG_USERS_EXTERNAL')
from config import TAG_STORAGE
from config import TAG_VARS
from config import TAG_IS_FILE
USERS_TAGS_prefix              = os.getenv('USERS_TAGS_prefix')

# redis
REDIS_URL = os.getenv('REDIS_URL')

# paths
UPLOAD_PATH = FLASKAPP_PATH
UPLOAD_DIR  = os.getenv('UPLOAD_DIR')

# secrets, tokens
JWT_SECRET_VERIFY_EMAIL   = os.getenv('JWT_SECRET_VERIFY_EMAIL')
JWT_SECRET_PASSWORD_RESET = os.getenv('JWT_SECRET_PASSWORD_RESET')

# cors
IO_CORS_ALLOW_ORIGINS = (
  os.getenv('IOCORS_ALLOW_ORIGIN_dev'),
  os.getenv('IOCORS_ALLOW_ORIGIN_dev2'),
  os.getenv('IOCORS_ALLOW_ORIGIN_dev3'),
  os.getenv('IOCORS_ALLOW_ORIGIN_dev4'),
  os.getenv('IOCORS_ALLOW_ORIGIN_dev5'),
  os.getenv('IOCORS_ALLOW_ORIGIN_dev6'),
  os.getenv('IOCORS_ALLOW_ORIGIN_nikolavrs'),
  os.getenv('IOCORS_ALLOW_ORIGIN_frikomnikolavrs')
)

# io:events
IOEVENT_ACCOUNTS_UPDATED               = os.getenv('IOEVENT_ACCOUNTS_UPDATED')
IOEVENT_ACCOUNTS_UPDATED_prefix        = os.getenv('IOEVENT_ACCOUNTS_UPDATED_prefix')
IOEVENT_AUTH_NEWUSER                   = os.getenv('IOEVENT_AUTH_NEWUSER')
IOEVENT_DOCS_CHANGE_JsonData           = os.getenv('IOEVENT_DOCS_CHANGE_JsonData')
IOEVENT_REDIS_CACHE_KEY_UPDATED_prefix = os.getenv('IOEVENT_REDIS_CACHE_KEY_UPDATED_prefix')
IOEVENT_COLLECTIONS_UPSERT_prefix      = os.getenv('IOEVENT_COLLECTIONS_UPSERT_prefix')

# scheduler
SCHEDULER_INIT                 = bool(os.getenv('SCHEDULER_INIT'))

# services
# redis
REDIS_INIT                     = bool(os.getenv('REDIS_INIT'))
SESSION_REDIS_INIT             = bool(os.getenv('SESSION_REDIS_INIT'))
#  firebase
CLOUD_MESSAGING_CERTIFICATE    = os.getenv('CLOUD_MESSAGING_CERTIFICATE')
CLOUD_MESSAGING_INIT           = bool(os.getenv('CLOUD_MESSAGING_INIT'))
KEY_FCM_DEVICE_TOKENS          = os.getenv('KEY_FCM_DEVICE_TOKENS')
#  aws
AWS_END_USER_MESSAGING_ENABLED = bool(os.getenv('AWS_END_USER_MESSAGING_ENABLED'))
#  viber
URL_VIBER_MESSAGE_POST                 = os.getenv('URL_VIBER_MESSAGE_POST')
VIBER_CHANNELS_DOCID                   = os.getenv('VIBER_CHANNELS_DOCID')
VIBER_CHANNELS_CACHEID                 = os.getenv('VIBER_CHANNELS_CACHEID')
VIBER_CHANNELS_CACHEID_GLOBAL_CHANNELS = os.getenv('VIBER_CHANNELS_CACHEID_GLOBAL_CHANNELS')
VIBER_USER_CHANNELS_prefix             = os.getenv('VIBER_USER_CHANNELS_prefix')
URL_VIBER_SET_WEBHOOK                  = os.getenv('URL_VIBER_SET_WEBHOOK')
VIBER_URL_ACCOUNT_INFO                 = os.getenv('VIBER_URL_ACCOUNT_INFO')
# googlemaps
API_KEY_GOOGLE_MAPS_PLACES = os.getenv('API_KEY_GOOGLE_MAPS_PLACES')



# topics comms
TOPIC_CHAT_USER_CHANNEL_prefix = os.getenv('TOPIC_CHAT_USER_CHANNEL_prefix')
TOPIC_CHAT_ASSETS_prefix       = os.getenv('TOPIC_CHAT_ASSETS_prefix')


# assets :topics :tags
TAG_ASSETS_SHAREABLE_GLOBALY = os.getenv('TAG_ASSETS_SHAREABLE_GLOBALY')
CATEGORY_KEY_ASSETS_prefix   = os.getenv('CATEGORY_KEY_ASSETS_prefix')

# mongo:db
MONGO_DB_INIT = bool(os.getenv('MONGO_DB_INIT'))
MONGO_URI     = os.getenv('MONGO_URI')


# app:main
app = Flask(__name__)


# app-config
app.config['SECRET_KEY'] = APP_SECRET_KEY
app.config['MAX_BODY_SIZE']      = MAX_BODY_SIZE_MB * 1024 * 1024
app.config['MAX_CONTENT_LENGTH'] = app.config['MAX_BODY_SIZE']

# app-config:db
app.config['SQLALCHEMY_DATABASE_URI']        = DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO']                = not PRODUCTION or bool(os.getenv('SQLALCHEMY_ECHO'))

# app-config:email
app.config['MAIL_SERVER']            = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT']              = os.getenv('MAIL_PORT')
app.config['MAIL_USERNAME']          = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD']          = os.getenv('MAIL_PASSWORD')
app.config['MAIL_USE_TLS']           = bool(os.getenv('MAIL_USE_TLS'))
app.config['MAIL_USE_SSL']           = bool(os.getenv('MAIL_USE_SSL'))
app.config['MAIL_ASCII_ATTACHMENTS'] = bool(os.getenv('MAIL_ASCII_ATTACHMENTS'))

# app-config:redis
app.config['REDIS_URL'] = REDIS_URL

# app-config:mongo
app.config['MONGO_URI'] = MONGO_URI


CORS(app, 
  supports_credentials = True, 
  resources = {
    r'/auth'                  : {'origins': '*'},
    r'/graphql'               : {'origins': '*'},
    r'/storage'               : {'origins': '*'},
    r'/webhook_viber_channel' : {'origins': '*'},
    r'/b64url'                : {'origins': '*'},
  }
) if PRODUCTION else CORS(app, supports_credentials = True)


Talisman(app, 
  force_https = False)


redis_client = None
if REDIS_INIT:
  from config.redis import redis_init
  redis_client = redis_init(app)

if SESSION_REDIS_INIT:
  from config.session_redis import session_redis_init
  session_redis_init(app, redis = redis_client)


if CLOUD_MESSAGING_INIT:
  import config.cloud_messaging.app_init


if SCHEDULER_INIT:
  from config.scheduler import scheduler_configure
  scheduler_configure(app)


# api   = Api(app)
db    = SQLAlchemy(app, model_class = DbModelBaseClass)
io    = SocketIO(app, 
                  cors_allowed_origins = IO_CORS_ALLOW_ORIGINS, 
                  # cors_allowed_origins="*",
                  cors_supports_credentials = True,
                )
mail  = Mail(app)

# mongo client
mongo = PyMongo(app, uri = MONGO_URI) if MONGO_DB_INIT else None

# db schema
with app.app_context():

  from models.tokens   import Tokens
  from models.tags     import Tags
  from models.docs     import Docs
  from models.users    import Users
  from models.assets   import Assets
  from models.orders   import Orders

  # drop/create schema
  if REBUILD_SCHEMA:
    db.drop_all()
  
  # create schema
  db.create_all()

  # setup tables
  import config.init_tables


# mount resources
# from resources.docs import DocsResource
# api.add_resource(DocsResource, '/docs/<string:tag_name>')

from blueprints                       import bp_home
from blueprints.auth                  import bp_auth
from blueprints.storage               import bp_storage
from blueprints.webhook_viber_channel import bp_webhook_viber_channel
from blueprints.b64url                import bp_b64url

# @blueprints:mount
#   /
app.register_blueprint(bp_home)

#   /auth
app.register_blueprint(bp_auth)

#   /storage
app.register_blueprint(bp_storage)

# /webhook
app.register_blueprint(bp_webhook_viber_channel)

# /b64url
app.register_blueprint(bp_b64url)

if not PRODUCTION:
  #   /test
  from blueprints.testing import bp_testing
  app.register_blueprint(bp_testing)
  
# graphql endpoint, `POST /graphql`
import config.graphql.init
  

io.init_app(app)
# io status check
@io.on('connect')
def io_connected():
  print('@connection:io')


# authentication.middleware@init
from middleware.authenticate import authenticate
@app.before_request
def before_request_authenticate():
  return authenticate()

