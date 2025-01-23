from marshmallow import Schema
from marshmallow import fields as mfields
from marshmallow import INCLUDE

class SchemaValidateCollectionsConfig(Schema):
  class Meta:
    unknown = INCLUDE
  fields = mfields.List(mfields.String(), required = True)
  sort   = mfields.String()

