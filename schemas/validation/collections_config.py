from marshmallow import Schema
from marshmallow import fields
from marshmallow import INCLUDE

class SchemaValidateCollectionsConfig(Schema):
  class Meta:
    unknown = INCLUDE
  fields = fields.List(fields.String(), required = True)
