import os

from marshmallow import Schema
from marshmallow import validate
from marshmallow import fields
from marshmallow import INCLUDE

from utils.hex_rand import hex_rand


AUTH_PASSWORD_MIN_LENGTH = int(os.getenv('AUTH_PASSWORD_MIN_LENGTH'))

class SchemaAuthLogin(Schema):
  email    = fields.Email(required = True)
  password = fields.String(required = True)

class SchemaAuthRegister(Schema):
  email    = fields.Email(required = True)
  password = fields.String(required = True, 
                        validate = validate.Length(min = AUTH_PASSWORD_MIN_LENGTH))

class SchemaAuthSocial(Schema):

  class Meta:
    unknown = INCLUDE
  
  email       = fields.Email(required = True)
  uid         = fields.String()
  displayName = fields.String()
  photoURL    = fields.String()

class SchemaEmailResetRequest(Schema):
  url   = fields.String()
  email = fields.Email(required = True)

class SchemaEmailResetObnovaLozinke(Schema):
  key      = fields.String(required = True)
  password = fields.String(required = True)
