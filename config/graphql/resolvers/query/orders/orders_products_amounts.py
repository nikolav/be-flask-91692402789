
from config.graphql.init import query
from flask_app import db
from models.assets import Assets
# from models.assets import AssetsType
from models.orders import Orders
from models import ln_orders_products
from schemas.serialization import SchemaSerializeAssets


# ordersProductsAmounts(ooid: ID!): [Asset!]!
@query.field('ordersProductsAmounts')
def resolve_ordersProductsAmounts(_obj, _info, ooid):
  q = db.select(
      Assets, 
      ln_orders_products.c.amount,
    ).join(
      ln_orders_products
    ).join(
      Orders
    ).where(
      ooid == Orders.id)
  
  return [{ 
            'product': SchemaSerializeAssets(exclude = ('assets_has', 'author',)).dump(a),
            'amount' : amount,
          } for a, amount in db.session.execute(q)]
