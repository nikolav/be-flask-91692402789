
from config.graphql.init import mutation
from src.classes         import ResponseStatus
from flask_app           import db
from models.assets       import Assets
from models.assets       import AssetsType
from models.orders       import Orders
from flask               import g
from models              import ln_orders_products

from schemas.serialization import SchemaSerializeOrders


# catalogOrderAdd(sid: ID!, items: JsonData!): JsonData!
@mutation.field('catalogOrderAdd')
def resolve_catalogOrderAdd(_obj, _info, sid, items):
  # items: {[pid:ID]: amount:number}
  r = ResponseStatus()
  o = None
  
  try:
    s = db.session.scalar(
      db.select(
        Assets
      ).where(
        sid == Assets.id,
        AssetsType.PHYSICAL_STORE.value == Assets.type
      ))
    pls = [p for p in Assets.by_ids_and_type(*items.keys(), type = AssetsType.PHYSICAL_PRODUCT.value)]
    o = Orders(
      author   = g.user,
      site     = s,
      products = pls,
    )
    db.session.add(o)
    db.session.commit()
    
    for p in pls:
      db.session.execute(
        db.update(
          ln_orders_products
        ).where(
          o.id == ln_orders_products.c.order_id,
          p.id == ln_orders_products.c.product_id,
        ).values(
          amount = items.get(str(p.id))
        ))
    db.session.commit()


  except Exception as err:
    r.error = err
  
  
  else:
    r.status = { 
                  'id'    : o.id, 
                  'order' : SchemaSerializeOrders(exclude = ('products', 'author', 'site',)).dump(o),
                }

  return r.dump()


