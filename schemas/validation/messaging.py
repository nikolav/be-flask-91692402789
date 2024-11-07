
from marshmallow import Schema
from marshmallow import fields


class SchemaValidateMessage(Schema):
  title = fields.String(required = True)
  body  = fields.String(required = True)

class SchemaValidateNotificationMessage(SchemaValidateMessage):
  image = fields.String()

class SchemaChatMessage(Schema):
  uid     = fields.Integer()
  name    = fields.String()
  message = fields.String(required = True)

