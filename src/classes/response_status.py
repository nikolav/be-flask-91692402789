
import json

from marshmallow import fields
from marshmallow import Schema


class _SchemaResponseStatus(Schema):
  error  = fields.Method('resolve_error')
  status = fields.Method('resolve_status')

  def resolve_error(self, node):
    err_ = getattr(node, 'error')
    return str(err_) if None != err_ else None

  def resolve_status(self, node):
    return getattr(node, 'status')


class ResponseStatus():
  def __init__(self):
    self.error  = None
    self.status = None
  
  def dump(self):
    return _SchemaResponseStatus().dump(self)
  
  def __repr__(self):
    return json.dumps(self.dump())


