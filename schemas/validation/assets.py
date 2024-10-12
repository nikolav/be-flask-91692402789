
from marshmallow import Schema
from marshmallow import fields
from marshmallow import EXCLUDE


class SchemaInputAssetsAdd(Schema):
  class Meta:
    unknown = EXCLUDE
  
  code      = fields.String()
  location  = fields.String()
  status    = fields.String()
  condition = fields.String()
  notes     = fields.String()
  data      = fields.Dict()


class SchemaInputAssets(SchemaInputAssetsAdd):
  name = fields.String()
  type = fields.String()


class SchemaInputAssetsCreate(SchemaInputAssetsAdd):
  name = fields.String(required = True)
  type = fields.String(required = True)


