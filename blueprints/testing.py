from flask       import Blueprint
from flask_cors  import CORS

from src.classes import ResponseStatus


bp_testing = Blueprint('testing', __name__, url_prefix = '/test')

# cors blueprints as wel for cross-domain requests
CORS(bp_testing)

@bp_testing.route('/', methods = ('POST',))
def testing_home():  
  from sqlalchemy import func
  from sqlalchemy import or_
  from sqlalchemy import and_
  from sqlalchemy import literal
  from sqlalchemy import union
  from flask import g
  from flask_app import db
  # from models.users import Users
  from models.assets import Assets
  from models.assets import AssetsType
  from models.assets import AssetsStatus
  from models.users import Users
  # from sqlalchemy import func
  from schemas.serialization import SchemaSerializeAssetsTextSearch

  r = ResponseStatus()

  return r.dump()

