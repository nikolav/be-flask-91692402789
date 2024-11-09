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
  # fields
  id        = fields.Integer()
  email     = fields.String()
  password  = fields.String()
  profile   = fields.Dict()

  # virtual
  tags      = fields.List(fields.String())
  products  = fields.List(fields.Nested(lambda: SchemaSerializeProductsTimes(exclude = ('user',))))
  posts     = fields.List(fields.Nested(lambda: SchemaSerializePosts(exclude = ('user',))))
  
  # computed
  is_approved    = fields.Method('calc_is_approved')
  is_manager     = fields.Method('calc_is_manager')
  is_admin       = fields.Method('calc_is_admin')
  is_external    = fields.Method('calc_is_external')
  groups         = fields.Method('calc_groups')
  email_verified = fields.Method('calc_email_verified')
  is_available   = fields.Method('calc_is_available')


  def calc_is_available(self, u):
    return u.is_available()
  
  def calc_groups(self, u):
    return [g.name for g in u.groups()]
  
  def calc_is_approved(self, u):
    return u.approved()
  
  def calc_is_manager(self, u):
    return u.is_manager()
  
  def calc_is_admin(self, u):
    return u.is_admin()
  
  def calc_is_external(self, u):
    return u.is_external()

  def calc_email_verified(self, u):
    return u.email_verified()
    

class SchemaSerializeUsersWho(SchemaSerializeTimes):

  # fields
  id      = fields.Integer()
  email   = fields.String()
  profile = fields.Dict()
  
  # computed
  admin          = fields.Method('calc_admin')
  approved       = fields.Method('calc_approved')
  email_verified = fields.Method('calc_email_verified')
  external       = fields.Method('calc_is_external')
  manager        = fields.Method('calc_manager')


  def calc_approved(self, u):
    return u.approved()
  
  def calc_admin(self, u):
    return u.is_admin()

  def calc_email_verified(self, u):
    return u.email_verified()
  
  def calc_manager(self, u):
    return u.is_manager()
  
  def calc_is_external(self, u):
    return u.is_external()

  
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
  data      = fields.Dict()
  notes     = fields.String()
  
  # virtal
  # users = fields.List(fields.Nested(SchemaSerializeUsersTimes(exclude = ('password',))))
  tags       = fields.List(fields.String())
  author     = fields.Nested(SchemaSerializeUsersTimes(exclude = ('password', 'posts', 'products')))
  users      = fields.List(fields.Nested(SchemaSerializeUsersTimes(exclude = ('password', 'posts', 'products'))))
  docs       = fields.List(fields.Nested(SchemaSerializeDocJsonTimes()))
  assets_has = fields.List(fields.Nested(lambda: SchemaSerializeAssets(exclude = ('assets_has',))))

class SchemaSerializeUsersTextSearch(Schema):
  email               = fields.String()
  tags                = fields.Method('tags_joined')
  groups              = fields.Method('groups_joined')
  profile_firstName   = fields.Method('pull_profile_firstName')
  profile_lastName    = fields.Method('pull_profile_lastName')
  profile_displayName = fields.Method('pull_profile_displayName')
  profile_job         = fields.Method('pull_profile_job')


  def pull_profile_firstName(self, user):
    return user.get_profile().get('firstName')

  def pull_profile_lastName(self, user):
    return user.get_profile().get('lastName')

  def pull_profile_displayName(self, user):
    return user.get_profile().get('displayName')

  def pull_profile_job(self, user):
    return user.get_profile().get('job')

  def tags_joined(self, user):
    return ' '.join([t.tag for t in user.tags])

  def groups_joined(self, user):
    ug = user.groups()
    return ' '.join([g.name for g in ug])

'''
{
  "email": "admin@nikolav.rs",
  "profile": {
    "firstName": "Nikola",
    "lastName": "Vukovic",
    "phone": "066 572 55 23",
    "address": "mihaila milovanovica 76v, 11400 mladenovac",
    "displayName": "nikolav",
    "displayLocation": "Aenean ut eros et",
    "job": "mercha",
    "employed_at": "2024-11-04T23:00:00+00:00",
    "avatarImage": "https://firebasestorage.googleapis.com/v0/b/jfejcxjyujx.appspot.com/o/media%2FAVATARS%3AyenDhzULhtZohA9yo%2F1%2FavatarImage?alt=media&token=ef4f4b83-f1ae-49ef-99c5-39567fb7b636"
  },
  "tags": [
    "@policy:admins:ext0ZRQE9gmZ8Bvwb8GMq5DNmh8wEF",
    "@policy:managers:Bc0b4kk",
    "@policy:email:HRcEBSaJNx1HQfrzq5DNmh8wEF",
    "@policy:storage:fDixi7hFsnq5DNmh8wEF",
    "@policy:approved:r1loga1PP4",
    "email-verified:hba0P",
    "USERS_TAGS:6yXEQ5lK4e38jPN1:admins",
    "foo",
    "bar",
    "baz"
  ],
  "groups": [
    "Lorem Ipsums",
    "Phasellus",
    "Cras non",
    "Nullam vel sem"
  ]
}
'''