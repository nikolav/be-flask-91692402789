
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
      raise ValidationError('@pagination.page: must be gt:0')
  
  @validates('page')
  def validates_page(self, value):
    if not 0 < value:
      raise ValidationError('@pagination.per_page: must be gt:0')

