from flask_app             import db
from models.assets         import Assets
from models.assets         import AssetsType
from config.graphql.init   import query
from schemas.serialization import SchemaSerializeAssets


@query.field('productsList')
def resolve_productsList(_obj, _info, pids = None):
  q_products = db.select(
    Assets
  ).where(
    AssetsType.PHYSICAL_PRODUCT.value == Assets.type)
      
  # q:chain
  if None != pids:
    q_products = q_products.where(
      Assets.id.in_(pids))
  
  products = db.session.scalars(q_products)
  
  return SchemaSerializeAssets(many = True).dump(products)

