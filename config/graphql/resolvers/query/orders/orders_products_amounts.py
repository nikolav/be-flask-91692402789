
from config.graphql.init import query
from flask_app import db
from models.assets import Assets
# from models.assets import AssetsType
from models.orders import Orders
from models import ln_orders_products
from schemas.serialization import SchemaSerializeAssets
from schemas.serialization import SchemaSerializeOrders


# ordersProductsAmounts(ooid: ID!): OrderItems!
@query.field('ordersProductsAmounts')
def resolve_ordersProductsAmounts(_obj, _info, ooid):
  # {order:IOrders; items:{amount:number; product:Assets}[]}

  r = { 'order': None, 'items': [] }
  o = db.session.get(Orders, ooid)

  if o:
    q = db.select(
        Assets, 
        ln_orders_products.c.amount,
      ).join(
        ln_orders_products
      ).join(
        Orders
      ).where(
        ooid == Orders.id)
    
    r['order'] = SchemaSerializeOrders().dump(o)
    r['items'] = [{ 
                    'amount' : amount,
                    'product': SchemaSerializeAssets(exclude = ('assets_has', 'author',)).dump(a),
                  } for a, amount in db.session.execute(q)]
  
  return r

