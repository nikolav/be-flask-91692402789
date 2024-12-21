
from config.graphql.init   import query
from flask_app             import db
from models.assets         import Assets
from models.assets         import AssetsType
from models.orders         import Orders
from schemas.serialization import SchemaSerializeOrders


# assetsAssetsSitesOrders(sid: ID!): [Orders!]!
@query.field('assetsAssetsSitesOrders')
def resolve_assetsAssetsSitesOrders(_obj, _info, sid):
  q = db.select(
        Orders
      ).join(
        Orders.site
      ).where(
        AssetsType.PHYSICAL_STORE.value == Assets.type,
        sid == Assets.id
      ).order_by(
        Orders.created_at.desc())
  
  lso = db.session.scalars(q)
  
  
  return SchemaSerializeOrders(many = True).dump(lso)

