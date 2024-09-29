
from flask import g

from flask_app import db
from flask_app import JWT_SECRET_VERIFY_EMAIL
from flask_app import io
from flask_app import IOEVENT_ACCOUNTS_UPDATED_prefix

from models.users        import Users
from config.graphql.init import mutation
from utils.jwtToken      import decode_secret


@mutation.field('accountsVeifyEmail')
def resolve_accountsVeifyEmail(_o, _i, data):

  r        = { 'error': None, 'status': None }
  verified = None
  id       = None

  try:
    # .uid .email
    payload = decode_secret(data.get('key'), 
                            JWT_SECRET_VERIFY_EMAIL)
    u = db.session.get(Users, payload['uid'])
    
    if not u:
      raise Exception('accountsVeifyEmail --no-user')

    if not u.id == g.user.id:
      raise Exception('accountsVeifyEmail --access-denied')
    
    verified = u.set_email_verified(True)

    # affected row-id
    if verified:
      id = u.id

    
  except Exception as err:
    r['error'] = str(err)
    
  
  else:
    r['status'] = { 'email': u.email if verified else None }
    if id:
      io.emit(f'{IOEVENT_ACCOUNTS_UPDATED_prefix}{id}')
  

  return r


