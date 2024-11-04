
from enum import Enum

from marshmallow import fields

from .auth        import SchemaAuthRegister
from models.users import UsersPolicies


class EPolicies(Enum):
  admin    = UsersPolicies.ADMINS.value
  external = UsersPolicies.EXTERNAL.value


class SchemaAccountsAddCredentialsPayload(SchemaAuthRegister):
  policies = fields.List(fields.Enum(EPolicies))

