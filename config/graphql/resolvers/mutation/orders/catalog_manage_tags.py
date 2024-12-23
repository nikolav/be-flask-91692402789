
from config.graphql.init   import mutation
from src.classes           import ResponseStatus
from flask_app             import db
from flask_app             import io
from models.orders         import Orders
from models.orders         import OrdersIOEvents
from schemas.serialization import SchemaSerializeOrders


# catalogManageTags(id: ID!, config: JsonData!): JsonData!
@mutation.field('catalogManageTags')
def resolve_catalogManageTags(_obj, _info, id, config):
  # config: { [string:tag-name]: boolean:add-remove-flag }
  changes = 0
  r = ResponseStatus()
  o = None

  tls_add = None
  tls_rm  = None

  try:
    if config:
      o = db.session.get(Orders, id)
      if not o:
        raise Exception(f'order:#{id}:not-found')
      
      tls_add = [t for t, flag in config.items() if True  == flag]
      tls_rm  = [t for t, flag in config.items() if False == flag]

      changes += o.tags_add(*tls_add, _commit = False)
      changes += o.tags_rm(*tls_rm,   _commit = False)

      if 0 < changes:
        db.session.commit()


  except Exception as err:
    r.error = err
  

  else:
    r.status = { 
                'id'           : o.id, 
                'order'        : SchemaSerializeOrders(exclude = ('products',)).dump(o),
                'changes'      : changes, 
                'tags_added'   : tls_add, 
                'tags_removed' : tls_rm,
              }
    if 0 < changes:
      io.emit(f'{OrdersIOEvents.IOEVENT_ORDERS_CONFIGRED_prefix.value}{o.id}')


  return r.dump()
  
