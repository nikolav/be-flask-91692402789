
from config.graphql.init import query

from flask_app import db
from models.assets import Assets
from models.assets import AssetsStatus

from sqlalchemy import or_
from sqlalchemy import and_
from sqlalchemy import func
from sqlalchemy import literal
# from sqlalchemy import union

from  src.classes import ResponseStatus


# assetsCount(asset_type: String!, own: Boolean): Int!
@query.field('assetsCount')
def resolve_assetsCount(_, _info, asset_type, own = False):
  r = ResponseStatus()

  try:
    q_nonarchived = or_(
      Assets.status.is_(None),
      and_(
        Assets.status.is_not(None),
        AssetsStatus.ARCHIVED.value != Assets.status
      ))
    
    q = db.select(
      literal(asset_type).label('asset'),
      func.count(Assets.id).label('count')
    ).where(
      asset_type == Assets.type,
      q_nonarchived)
    
    r.status = { 'count': {      
                    node.asset: node.count 
                      for node in db.session.execute(q)
                  }}
    
  except Exception as err:
    r.error = err
  
  return r.dump()

