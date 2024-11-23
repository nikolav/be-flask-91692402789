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
  
  q_nonarchived = or_(
      Assets.status.is_(None),
      and_(
        Assets.status.is_not(None),
        AssetsStatus.ARCHIVED.value != Assets.status
      )
    )
  
  q_count_products = db.select(
    literal('products').label('asset'),
    func.count(Assets.id).label('tot')
  ).where(
    AssetsType.PHYSICAL_PRODUCT.value == Assets.type,
    q_nonarchived)
  # q_count_groups = db.select(
  #   literal('groups').label('asset'),
  #   func.count(Assets.id).label('tot')
  # ).where(
  #   AssetsType.PEOPLE_GROUP_TEAM.value == Assets.type,
  #   q_nonarchived)
  # q_count_sites = db.select(
  #   literal('sites').label('asset'),
  #   func.count(Assets.id).label('tot')
  # ).where(
  #   AssetsType.PHYSICAL_STORE.value == Assets.type,
  #   q_nonarchived)
  
  q = union(
    q_count_products, 
    # q_count_groups, 
    # q_count_sites,
  )

  r.status = { 
              node.asset: node.tot 
                for node in db.session.execute(q)
              }

  return r.dump()

