from marshmallow import Schema
from marshmallow import fields

# https://marshmallow.readthedocs.io/en/stable/quickstart.html#field-validators-as-methods



class SchemaSerializeTimes(Schema):
  created_at = fields.DateTime()
  updated_at = fields.DateTime()

class SchemaSerializeDocJson(Schema):
  id   = fields.Int()
  data = fields.Dict()


class SchemaSerializeDocJsonTimes(SchemaSerializeDocJson):
  created_at = fields.DateTime()
  updated_at = fields.DateTime()  

# 1
class SchemaSerializeDocJsonWithRelationsPosts(SchemaSerializeDocJsonTimes):
  post = fields.Nested(lambda: SchemaSerializePosts(exclude = ('docs',)))

class SchemaSerializeUsersTimes(SchemaSerializeTimes):
  id          = fields.Integer()
  email       = fields.String()
  password    = fields.String()
  products    = fields.List(fields.Nested(lambda: SchemaSerializeProductsTimes(exclude = ('user',))))
  posts       = fields.List(fields.Nested(lambda: SchemaSerializePosts(exclude = ('user',))))
  is_approved = fields.Method("calc_is_approved")

  def calc_is_approved(self, u):
    return u.approved()

class SchemaSerializeUsersWho(SchemaSerializeTimes):
  id             = fields.Integer()
  email          = fields.String()
  admin          = fields.Method('calc_admin')
  approved       = fields.Method('calc_approved')
  email_verified = fields.Method('calc_email_verified')

  def calc_approved(self, u):
    return u.approved()
  
  def calc_admin(self, u):
    return u.is_admin()

  def calc_email_verified(self, u):
    return u.email_verified()
  
class SchemaSerializeProductsTimes(SchemaSerializeTimes):
  id            = fields.Integer()
  user_id       = fields.Integer(dump_default = None)
  name          = fields.String()
  price         = fields.Float()
  description   = fields.String()
  stockType     = fields.String()
  stock         = fields.Float()
  onSale        = fields.Boolean()
  price_history = fields.List(fields.Dict())
  tags          = fields.List(fields.String())
  user          = fields.Nested(SchemaSerializeUsersTimes(exclude = ('password', 'products', 'posts')))
  docs          = fields.List(fields.Nested(SchemaSerializeDocJsonTimes()))


class SchemaSerializeOrdersTimes(SchemaSerializeTimes):
  user_id     = fields.Integer(dump_default = None)
  id          = fields.Integer()
  code        = fields.String()
  description = fields.String()
  completed   = fields.Boolean()
  canceled    = fields.Boolean()
  status      = fields.Integer()
  delivery_at = fields.DateTime()

class SchemaSerializeOrdersProducts(SchemaSerializeOrdersTimes):
  products = fields.List(fields.Nested(SchemaSerializeProductsTimes()))
  
# class SchemaSerializePosts(SchemaSerializeTimes):
#   id       = fields.Integer()
#   title    = fields.String()
#   content  = fields.String()

class SchemaSerializePosts(SchemaSerializeTimes):
  id          = fields.Integer()
  title       = fields.String()
  content     = fields.String()
  user_id     = fields.Integer()
  user        = fields.Nested(SchemaSerializeUsersTimes(exclude = ('password', 'posts', 'products')))
  tags        = fields.List(fields.String())
  docs        = fields.List(fields.Nested(SchemaSerializeDocJsonWithRelationsPosts(exclude = ('post',))))

class SchemaSerializeAssets(SchemaSerializeTimes):
  id        = fields.Integer()
  name      = fields.String()
  code      = fields.String()
  type      = fields.String()
  location  = fields.String()
  status    = fields.String()
  condition = fields.String()
  meta      = fields.Dict()
  notes     = fields.String()
  
  # virtal
  # users = fields.List(fields.Nested(SchemaSerializeUsersTimes(exclude = ('password',))))
  users = fields.List(fields.Nested(SchemaSerializeUsersTimes(exclude = ('password', 'posts', 'products'))))
  tags  = fields.List(fields.String())
  docs  = fields.List(fields.Nested(SchemaSerializeDocJsonTimes()))


