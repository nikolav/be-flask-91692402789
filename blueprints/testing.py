from flask       import Blueprint
from flask_cors  import CORS

from src.classes import ResponseStatus


bp_testing = Blueprint('testing', __name__, url_prefix = '/test')

# cors blueprints as wel for cross-domain requests
CORS(bp_testing)

@bp_testing.route('/', methods = ('POST',))
def testing_home():  
  from flask import g
  from flask_app import db
  # from models.users import Users
  from models.assets import Assets
  # from models.assets import AssetsType
  from models.users import Users
  # from sqlalchemy import func
  from schemas.serialization import SchemaSerializeUsersTimes
  from schemas.serialization import SchemaSerializeAssets

  r = ResponseStatus()
  
  u = db.session.get(Users, 1)

  r.status = { 'sites': SchemaSerializeAssets(many = True, exclude = ('assets_has',)).dump(
    u.related_assets_sites_managed(
        WITH_OWN = False,
      )
  ) }



  return r.dump()

