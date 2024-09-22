
from marshmallow import Schema
from marshmallow import fields


class SchemaValidateMessage(Schema):
  title = fields.String(required = True)
  body  = fields.String(required = True)

