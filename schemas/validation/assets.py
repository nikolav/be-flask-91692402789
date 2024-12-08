
from marshmallow import Schema
from marshmallow import fields
from marshmallow import EXCLUDE


class SchemaInputAssetsAdd(Schema):
  class Meta:
    unknown = EXCLUDE
  
  code      = fields.String()
  location  = fields.String()
  status    = fields.String(allow_none = True)
  condition = fields.String()
  notes     = fields.String()
  data      = fields.Dict()
  # 
  category  = fields.String()


# class SchemaInputAssets(SchemaInputAssetsAdd):
#   name = fields.String()
#   type = fields.String()


class SchemaInputAssetsCreate(SchemaInputAssetsAdd):
  name = fields.String(required = True)
  type = fields.String(required = True)


