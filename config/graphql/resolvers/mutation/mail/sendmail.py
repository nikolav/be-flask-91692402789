from flask      import render_template
from flask_mail import Message

from flask_app import mail
from flask_app import APP_NAME
from flask_app import APP_DOMAIN

from config              import MAIL_RECIPIENTS
from config.graphql.init import mutation


@mutation.field('sendmail')
def resolve_sendmail(_o, _i, subject, template, data):
  res   = None
  error = None

  try:
    res = mail.send(
      Message(
        # subject
        subject,

        # from
        sender = (APP_NAME, f'{APP_NAME}@{APP_DOMAIN}'),
        
        # default recepiens ls
        recipients = MAIL_RECIPIENTS,

        # pass all data to mail template
        html = render_template(f'mail/{template}.html', data = data)
      )
    )
    
  except Exception as err:
    error = err

  else:
    return { 'status': 'ok' if not res else str(res) }
  
  return { 'error': str(error) }
