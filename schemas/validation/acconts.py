from .auth import SchemaAuthRegister
from marshmallow import fields


from enum         import Enum
from models.users import UsersPolicies


class EPolicies(Enum):
  admin    = UsersPolicies.ADMINS.value
  manager  = UsersPolicies.MANAGERS.value
  external = UsersPolicies.EXTERNAL.value


class SchemaAccountsAddCredentialsPayload(SchemaAuthRegister):
  policies = fields.List(fields.Enum(EPolicies))

