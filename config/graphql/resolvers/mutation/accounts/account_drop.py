from flask import g

from flask_app import db
from flask_app import io
from flask_app import IOEVENT_ACCOUNTS_UPDATED

from models          import ln_users_tags
from models          import ln_users_assets
from models.users    import Users
from models.docs     import Docs
from models.assets   import Assets

from config.graphql.init import mutation
from src.classes         import ResponseStatus

from utils.jwtToken import setInvalid as token_set_invalid


@mutation.field('accountsDrop')
def resollve_accountsDrop(_o, _i, uid):
  '''
    drops 
      Users.id
      related records 
        --Tags --Docs
  '''
  r  = ResponseStatus()
  id = None

  
  try:
    u = db.session.get(Users, uid)

    # if account exists
    if u:

      if not g.user.can_manage_account(u.id):
        raise Exception('accountsDrop --access-denied')
        
      id = u.id
      
      db.session.execute(
        db.delete(
          ln_users_tags
        ).where(
          id == ln_users_tags.c.user_id
        ))
                          
      db.session.execute(
        db.delete(
          Docs
        ).where(
          id == Docs.user_id
        ))
      
      db.session.execute(
        db.delete(
          ln_users_assets
        ).where(
          id == ln_users_assets.c.user_id
        ))
      
      # clear related assets
      #  set group.author_id = None
      db.session.execute(
        db.update(
          Assets
        ).where(
          uid == Assets.author_id,
        ).values(
          author_id = None
        ))
      
      db.session.execute(
        db.delete(
          Users
        ).where(
          id == Users.id
        ))
      
      db.session.commit()

      # Users.clear_storage(uid)

      # if not g.user.is_admin():
      #   token_set_invalid(g.access_token)
    
    
  except Exception as err:
    raise err
    r.error = err
    

  else:
    r.status = { 'id': id }
    if id:
      io.emit(IOEVENT_ACCOUNTS_UPDATED)
  

  return r.dump()

