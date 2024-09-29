
from flask import g
from flask import render_template

from flask_mail import Message

from flask_app import db
from flask_app import mail

from models.users import Users

from utils.jwtToken      import encode_secret
from config.graphql.init import mutation

from flask_app import APP_NAME
from flask_app import APP_DOMAIN
from flask_app import JWT_SECRET_VERIFY_EMAIL


@mutation.field('accountsSendVerifyEmailLink')
def resolve_accountsSendVerifyEmailLink(_o, _i, uid, url):
  r   = { 'error': None, 'status': None }
  res = None
  
  try:
    u = db.session.get(Users, uid)

    if not u:
      raise Exception('accountsSendVerifyEmailLink --no-user')

    if not u.id == g.user.id:
      raise Exception('accountsSendVerifyEmailLink --access-denied')

    if u.email_verified():
      raise Exception('accountsSendVerifyEmailLink --email-verified')
      
        
    key = encode_secret({ 'uid': u.id, 'email': u.email }, 
                        JWT_SECRET_VERIFY_EMAIL)
    
    res = mail.send(
      Message(
        
        # subject
        f'Potvrda email adrese | {APP_DOMAIN}',

        # from
        sender = (APP_NAME, f'{APP_NAME}@{APP_DOMAIN}'),
        
        # default recepiens ls
        recipients = [u.email],
        
        # pass all data to mail template
        html = render_template(
          'mail/auth-verify-email.html', 
          url = f'{str(url).rstrip("/")}/?key={key}')
      )
    )
    

  except Exception as err:
    r['error'] = str(err)


  else:
    r['status'] = { 'id': u.id if not res else None }
  
  
  return r

