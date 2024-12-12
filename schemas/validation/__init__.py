
from marshmallow import Schema
from marshmallow import fields
from marshmallow import validates
from marshmallow import validate
from marshmallow import ValidationError

class SchemaInputPagination(Schema):
  page     = fields.Integer()
  per_page = fields.Integer()

  @validates('page')
  def validates_page(self, value):
    if not 0 < value:
      raise ValidationError('@SchemaInputPagination.page: must be gt:0')
  
  @validates('page')
  def validates_page(self, value):
    if not 0 < value:
      raise ValidationError('@SchemaInputPagination.per_page: must be gt:0')

class SchemaInputAssetsRows(Schema):
  strategy = fields.String(required = True)
  args     = fields.Dict()
  limit    = fields.Integer()
class SchemaInputAssetsRowsArgsOlderThan(Schema):
  older_than = fields.DateTime()
