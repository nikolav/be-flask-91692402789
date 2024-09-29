from flask import g

from flask_app import db
from flask_app import io
from flask_app import IOEVENT_ACCOUNTS_UPDATED

from models          import ln_users_tags
# from models          import ln_orders_products
# from models          import ln_products_tags
from models.users    import Users
from models.docs     import Docs
# from models.orders   import Orders
# from models.products import Products
# from models.posts    import Posts

from config.graphql.init import mutation

from utils.jwtToken import setInvalid as token_set_invalid


@mutation.field('accountsDrop')
def resollve_accountsDrop(_o, _i, uid):
  '''
    drops 
      Users.id
      related records 
        --Tags --Docs
  '''
  r  = { 'error': None,  'status': None }
  id = None
  
  try:
    u = db.session.get(Users, uid)

    # if account exists
    if u:

      if not g.user.can_manage_account(u.id):
        raise Exception('accountsDrop --access-denied')
        
      id = u.id

      # subq_oids = db.select(Orders.id).where(Orders.user_id == uid).subquery()
      # subq_pids = db.select(Products.id).where(Products.user_id == uid).subquery()
      
      # db.session.execute(
      #   db.delete(ln_orders_products)
      #     .where(ln_orders_products.c.order_id.in_(subq_oids))
      # ) 
      # db.session.execute(
      # db.delete(Orders)
      #   .where(
      #     Orders.user_id == uid
      #   )
      # )

      # db.session.execute(
      #   db.delete(ln_products_tags)
      #     .where(ln_products_tags.c.product_id.in_(subq_pids))
      # ) 
      # db.session.execute(
      #   db.delete(ln_orders_products)
      #     .where(ln_orders_products.c.product_id.in_(subq_pids))
      # ) 
      # db.session.execute(
      #   db.delete(Products)
      #   .where(
      #     Products.user_id == uid
      #   )
      # )
      
      db.session.execute(
        db.delete(
          ln_users_tags
        ).where(
          id == ln_users_tags.c.user_id
        ))
      
      # db.session.execute(
      #   db.delete(Posts)
      #     .where(
      #       Posts.user_id == uid
      #     )
      # )
      
      db.session.execute(
        db.delete(
          Docs
        ).where(
          id == Docs.user_id
        ))
      
      db.session.execute(
        db.delete(
          Users
        ).where(
          id == Users.id
        ))
      
      db.session.commit()

      # Users.clear_storage(uid)

      if not g.user.is_admin():
        token_set_invalid(g.access_token)
    
    
  except Exception as err:
    r['error'] = str(err)
    

  else:
    r['status'] = { 'id': id }
    if id:
      io.emit(IOEVENT_ACCOUNTS_UPDATED)
  

  return r

