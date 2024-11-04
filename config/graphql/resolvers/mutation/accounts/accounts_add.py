
from config.graphql.init  import mutation
from middleware.authguard import authguard
from flask_app            import io
from flask_app            import POLICY_ADMINS
from flask_app            import IOEVENT_ACCOUNTS_UPDATED
from models.users         import Users

from marshmallow import EXCLUDE
from schemas.validation.acconts import SchemaAccountsAddCredentialsPayload
from schemas.serialization      import SchemaSerializeUsersTimes

from src.classes import ResponseStatus


@mutation.field('accountsAdd')
@authguard(POLICY_ADMINS)
def resolve_accountsAdd(_obj, _inf, payload):
  r       = ResponseStatus()
  account = None

  try:
    credentials = SchemaAccountsAddCredentialsPayload(
      unknown = EXCLUDE, partial = ('policies',)).load(payload)
    account = Users.create_user(
      email    = credentials['email'],
      password = credentials['password'],
      policies = [e.value for e in credentials.get('policies', [])],
    )

    if not account:
      raise Exception('accountsAdd --failed')


  except Exception as err:
    r.error = err


  else:
    r.status = { 'account': SchemaSerializeUsersTimes(exclude = ('password',)).dump(account) }
    io.emit(IOEVENT_ACCOUNTS_UPDATED)


  return r.dump()

