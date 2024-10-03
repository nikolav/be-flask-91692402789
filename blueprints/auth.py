import secrets

from flask      import Blueprint
from flask      import g
from flask      import request
from flask      import render_template
from flask_cors import CORS
from flask_mail import Message

from flask_app      import db
from flask_app      import io
from flask_app      import mail

from models.users    import Users

from utils.pw       import hash  as hashPassword
from utils.pw       import check as checkPassword
from utils.jwtToken import issueToken
from utils.jwtToken import setInvalid as tokenSetInvalid
from utils.jwtToken import encode_secret
from utils.jwtToken import decode_secret

from middleware.arguments    import arguments_schema
from schemas.validation.auth import SchemaAuthLogin
from schemas.validation.auth import SchemaAuthRegister
from schemas.validation.auth import SchemaAuthSocial
from schemas.validation.auth import SchemaEmailResetRequest
from schemas.validation.auth import SchemaEmailResetObnovaLozinke
from schemas.serialization   import SchemaSerializeUsersWho

from flask_app import APP_NAME
from flask_app import APP_DOMAIN
from flask_app import JWT_SECRET_PASSWORD_RESET
from flask_app import IOEVENT_AUTH_NEWUSER

from flask_app import io
from flask_app import IOEVENT_ACCOUNTS_UPDATED_prefix



# router config
bp_auth = Blueprint('auth', __name__, url_prefix = '/auth')

# cors blueprints as wel for cross-domain requests
CORS(bp_auth)

@bp_auth.route('/register', methods = ('POST',))
@arguments_schema(SchemaAuthRegister())
def auth_register():

  email     = g.arguments['email']
  password  = g.arguments['password']
  
  token = ''
  error = '@error/auth:register'

  try:    
    # skip registered
    if (Users.email_exists(email)):
      raise Exception('auth_register:unavailable')

    # email available
    #  register, save
    newUser = Users.create_user(
      email    = email, 
      password = password,
    )
    
    # new user added, issue access-token
    token = issueToken({ 'id': newUser.id })
    
  except Exception as err:
    error = err
  
  else:
    # user registered, send token, 201
    if token:
      io.emit(IOEVENT_AUTH_NEWUSER)
      return { 'token': token }, 201
  
  # forbiden otherwise
  return { 'error': str(error) }, 403
  
@bp_auth.route('/login', methods = ('POST',))
@arguments_schema(SchemaAuthLogin())
def auth_login():
  email    = g.arguments['email']
  password = g.arguments['password']
  
  token   = ''
  error   = '@error/auth:login'
  
  try:
    # find user by `email`
    u = db.session.scalar(
      db.select(Users).where(Users.email == email)
    )
    
    # skip invalid credentials ~email ~password
    if not u:
      raise Exception('access denied')
    
    if not checkPassword(password, u.password):
      raise Exception('access denied')
    
    # app user valid here
    #  issue access token
    token = issueToken({ 'id': u.id })

  except Exception as err:
    error = err

  else:
    if token:
      return { 'token': token }, 200

  return { 'error': str(error) }, 401

@bp_auth.route('/social', methods = ('POST',))
def auth_social():
  # auth
  #   email
  #   uid?
  #   photoURL?
  #   displayName?
  token      = None
  user_added = None
  error      = None
  
  try:
    data      = request.get_json()
    auth_data = SchemaAuthSocial().load(data.get('auth'))
    
    # schema validated; authenticate authdata
    u = db.session.scalar(
      db.select(
        Users
      ).where(
        auth_data['email'] == Users.email
      ))
        
    if not u:
      u = Users.create_user(
        email    = auth_data['email'],
        # password = auth_data['uid'] if 'uid' in auth_data else secrets.token_bytes().hex(),
        password = auth_data['email'],
      )
      user_added = u.id
    
    # issue token
    token = issueToken({ 'id' : u.id })
          
    u.profile_update(patch = { 'authProvider': auth_data })
    db.session.commit()
          
  except Exception as err:
    error = err
  
  else:
    # auth social valid, send token, 201
    if user_added and token:
      io.emit(IOEVENT_AUTH_NEWUSER)
    
    return { 'token': token }, 201
  
  # forbiden otherwise
  return { 'error': str(error) }, 403

@bp_auth.route('/logout', methods = ('POST',))
def auth_logout():
  error = '@error/auth:logout'
  try:
    tokenSetInvalid(g.access_token)
  except Exception as err:
    error = err
  else:
    return {}, 200
  
  return { 'error': str(error) }, 500
  
@bp_auth.route('/who', methods = ('GET',))
def auth_who():
  error = '@error/auth:who'
  try:
    # send user data
    return SchemaSerializeUsersWho().dump(g.user), 200
  
  except Exception as err:
    error = err
  
  return { 'error': str(error) }, 500

@bp_auth.route('/password-reset-obnova-lozinke', methods = ('POST',))
def password_reset_obnova_lozinke():

  r       = { 'error': None, 'status': None }
  d       = None
  payload = None
  id      = None
  
  try:
    d       = SchemaEmailResetObnovaLozinke().load(request.get_json())
    payload = decode_secret(d['key'], 
                            JWT_SECRET_PASSWORD_RESET)

    u = db.session.scalar(
      db.select(
        Users
      ).where(
        payload['email'] == Users.email
      ))

    if not u:
      raise Exception('password_reset_obnova_lozinke --no-user')
    
    u.password = hashPassword(d['password'])
    db.session.commit()

    # affeced uid
    id = u.id

    
  except Exception as err:
    r['error'] = str(err)

    
  else:
    r['status'] = { 'id': id }
    if id:
      io.emit(f'{IOEVENT_ACCOUNTS_UPDATED_prefix}{id}')
  
  
  return r

@bp_auth.route('/password-reset-email-link', methods = ('POST',))
def password_reset_email_link():
  
  r   = { 'error': None, 'status': None }
  d   = None
  res = None

  try:
    d = SchemaEmailResetRequest().load(request.get_json())

    if not Users.email_exists(d['email']):
      raise Exception('password_reset_email_link --no-user')
    
    key = encode_secret({ 'email': d['email'] }, 
                          JWT_SECRET_PASSWORD_RESET)

    res = mail.send(
      Message(
        
        # subject
        f'obnova lozinke | {APP_DOMAIN}',

        # from
        sender = (APP_NAME, f'{APP_NAME}@{APP_DOMAIN}'),
        
        # default recepiens ls
        recipients = [d['email']],
        
        # pass all data to mail template
        html = render_template(
          'mail/password-reset-button-link.html', 
          url = f'{str(d['url']).rstrip("/")}/?key={key}')
      ))


  except Exception as err:
    r['error'] = str(err)
    

  else:
    r['status'] = { 'email': d['email'] if not res else None }
  
  
  return r

