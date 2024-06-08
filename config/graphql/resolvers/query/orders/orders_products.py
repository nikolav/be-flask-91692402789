from flask_app import db

from config.graphql.init import query

from models.orders   import Orders
from models.products import Products
from models          import ln_orders_products

from schemas.serialization import SchemaSerializeProductsTimes


@query.field('ordersProducts')
def resolve_ordersProducts(_obj, _info, oid):
  res = []

  try:

    r = db.session.execute(
      db.select(Products, ln_orders_products.c.amount)
        .join(ln_orders_products)
        .join(Orders)
        .where(
          Orders.id == oid
        )
    ).unique()
    
    for p, amount in r:
      node = SchemaSerializeProductsTimes().dump(p)
      node['amount'] = int(amount)
      res.append(node)

  except Exception as err:
    raise err
  
  return res
