
from config.graphql.init import mutation
from src.classes         import ResponseStatus
from models.orders       import Orders
from models              import ln_orders_products
from models              import ln_orders_tags
from flask_app           import db


# catalogOrderRemove(ids: [ID!]!): JsonData!
@mutation.field('catalogOrderRemove')
def resolve_catalogOrderRemove(_obj, _info, ids):
  r = ResponseStatus()

  try:
    db.session.execute(
      db.delete(
        ln_orders_tags
      ).where(
        ln_orders_tags.c.order_id.in_(ids)
      ))
    db.session.execute(
      db.delete(
        ln_orders_products
      ).where(
        ln_orders_products.c.order_id.in_(ids)
      ))
    db.session.execute(
      db.delete(
        Orders
      ).where(
        Orders.id.in_(ids)
      ))
    db.session.commit()


  except Exception as err:
    r.error = err


  else:
    r.status = 'ok'
    

  return r.dump()

