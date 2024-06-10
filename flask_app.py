import os

from dotenv           import load_dotenv
from flask            import Flask
from flask_restful    import Api
from flask_cors       import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_talisman   import Talisman
# https://github.com/miguelgrinberg/flask-socketio/issues/40#issuecomment-48268526
from flask_socketio import SocketIO
# https://pythonhosted.org/Flask-Mail/
from flask_mail import Mail

from src.classes import Base as DbModelBaseClass


load_dotenv()

ENV             = os.getenv('ENV')
PRODUCTION      = 'production' == ENV
APP_NAME        = os.getenv('APP_NAME')
DATABASE_URI    = os.getenv('DATABASE_URI_production') if PRODUCTION else os.getenv('DATABASE_URI_dev')
REBUILD_SCHEMA  = bool(os.getenv('REBUILD_SCHEMA'))
UPLOAD_PATH     = os.getenv('UPLOAD_PATH')
UPLOAD_DIR      = os.getenv('UPLOAD_DIR')

IO_CORS_ALLOW_ORIGINS = (
  os.getenv('IOCORS_ALLOW_ORIGIN_dev'),
  os.getenv('IOCORS_ALLOW_ORIGIN_nikolavrs'),
)


app = Flask(__name__)

# app-config
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

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


CORS(app, 
  supports_credentials = True, 
  resources = {
    r'/auth'    : {'origins': '*'},
    r'/graphql' : {'origins': '*'},
    r'/storage' : {'origins': '*'},
  }
) if PRODUCTION else CORS(app, supports_credentials = True)

Talisman(app, 
  force_https = False)


api   = Api(app)
db    = SQLAlchemy(app, model_class = DbModelBaseClass)
io    = SocketIO(app, 
                  cors_allowed_origins = IO_CORS_ALLOW_ORIGINS, 
                  # cors_allowed_origins="*",
                  cors_supports_credentials = True,
                )
mail  = Mail(app)


# init models
with app.app_context():

  from models.tokens   import Tokens
  from models.tags     import Tags
  from models.docs     import Docs
  from models.users    import Users
  from models.products import Products
  from models.orders   import Orders
  from models.posts    import Posts

  # drop/create schema
  if REBUILD_SCHEMA:
    db.drop_all()
  
  # create schema
  db.create_all()

  # init db
  import config.init_tables


# mount resources
from resources.docs import DocsResource
api.add_resource(DocsResource, '/docs/<string:tag_name>')

from blueprints         import bp_home
from blueprints.auth    import bp_auth
from blueprints.storage import bp_storage
# @blueprints:mount
#   /
app.register_blueprint(bp_home)
#   /auth
app.register_blueprint(bp_auth)
#   /storage
app.register_blueprint(bp_storage)
if not PRODUCTION:
  #   /test
  from blueprints.testing import bp_testing
  app.register_blueprint(bp_testing)
  
# init graphql endpoint, `POST /graphql`
import config.graphql.init
  

io.init_app(app)
# io status check
@io.on('connect')
def io_connected():
  print('@io/connection')


# authentication.middleware@init
from middleware.authenticate import authenticate
@app.before_request
def before_request_authenticate():
  return authenticate()

