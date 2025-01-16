
from marshmallow import Schema
from marshmallow import fields
from marshmallow import INCLUDE
# https://marshmallow.readthedocs.io/en/stable/quickstart.html#field-validators-as-methods

import json

from bson import ObjectId


class SchemaSerializeTimes(Schema):
  created_at = fields.DateTime()
  updated_at = fields.DateTime()

class SchemaSerializeDocJson(Schema):
  id   = fields.Integer()
  data = fields.Dict()
  key  = fields.String()


class SchemaSerializeDocJsonTimes(SchemaSerializeDocJson):
  created_at = fields.DateTime()
  updated_at = fields.DateTime()  


class SchemaSerializeUsersTimes(SchemaSerializeTimes):
  # fields
  id        = fields.Integer()
  email     = fields.String()
  password  = fields.String()
  profile   = fields.Dict()
  key       = fields.String()

  # virtual
  tags      = fields.List(fields.String())
  
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

  '''
    @schema:client schemaAuthData
  '''

  # fields
  id      = fields.Integer()
  email   = fields.String()
  profile = fields.Dict()
  key     = fields.String()
  
  # computed
  #  flags
  admin          = fields.Method('calc_admin')
  approved       = fields.Method('calc_approved')
  default        = fields.Method('calc_is_default')
  email_verified = fields.Method('calc_email_verified')
  external       = fields.Method('calc_is_external')
  manager        = fields.Method('calc_manager')
  #  fields
  groups         = fields.Method('calc_groups')

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

  def calc_is_default(self, u):
    return u.is_default_user()

  def calc_groups(self, u):
    return SchemaSerializeAssets(many = True, only = ('id', 'name')).dump(u.groups())


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
  key       = fields.String()
  author_id = fields.Integer()
  
  # virtal
  # users = fields.List(fields.Nested(SchemaSerializeUsersTimes(exclude = ('password',))))
  tags       = fields.List(fields.String())
  author     = fields.Nested(SchemaSerializeUsersTimes(exclude = ('password',)))
  users      = fields.List(fields.Nested(SchemaSerializeUsersTimes(exclude = ('password',))))
  docs       = fields.List(fields.Nested(SchemaSerializeDocJsonTimes()))
  assets_has = fields.List(fields.Nested(lambda: SchemaSerializeAssets(exclude = ('assets_has',))))

class SchemaSerializeUsersTextSearch(Schema):
  email               = fields.String()
  key                 = fields.String()
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


class SchemaSerializeAssetsTextSearch(Schema):
  name       = fields.String()
  code       = fields.String()
  location   = fields.String()
  notes      = fields.String()
  key        = fields.String()
  tags       = fields.Method('tags_joined')
  data_dumps = fields.Method('resolve_data_dumps')
  
  def tags_joined(self, asset):
    return ' '.join([t.tag for t in asset.tags])

  def resolve_data_dumps(self, asset):
    return json.dumps(asset.data) if None != asset.data else ''

class SchemaSerializeDocsQStringSearch(Schema):
  tags       = fields.Method('tags_joined')
  data_dumps = fields.Method('resolve_data_dumps')

  def tags_joined(self, d):
    from models.docs import DocsTags
    omit_tags = (
      DocsTags.TAGGED_CONTACTS.value,
    )
    return ' '.join([t.tag for t in d.tags if not t.tag in omit_tags])
  
  def resolve_data_dumps(self, d):
    return ' '.join([json.dumps(v) for v in d.data.values()]) if None != d.data else ''


class SchemaSerializeDocs(SchemaSerializeDocJsonTimes):
  # virtual
  asset = fields.Nested(SchemaSerializeAssets(
    exclude = ('assets_has', 'author', 'users', 'docs',)))
  user = fields.Nested(SchemaSerializeUsersTimes(
    exclude = ('password',)))
  tags = fields.List(fields.String())



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

class SchemaSerializeOrders(SchemaSerializeTimes):
  id     = fields.Integer()

  key    = fields.String()
  status = fields.String()
  data   = fields.Dict()
  notes  = fields.String()

  author_id = fields.Integer()
  site_id   = fields.Integer()
  
  # virtal
  author   = fields.Nested(SchemaSerializeUsersTimes(exclude = ('password',)))
  site     = fields.Nested(SchemaSerializeAssets(exclude = ('assets_has',)))
  tags     = fields.List(fields.String())
  products = fields.List(fields.Nested(SchemaSerializeAssets(exclude = ('assets_has', 'author',))))


# Custom field for handling ObjectId
class ObjectIdField(fields.Field):
  def _serialize(self, value, attr, obj, **kwargs):
    return str(value) if isinstance(value, ObjectId) else value

def schemaSerializeMongoDocument(*, FIELDS):
  class _SchemaSerializeMongoDbDocument(Schema):
    _id = ObjectIdField()
    class Meta:
      fields  = FIELDS
      unknown = INCLUDE
  
  return _SchemaSerializeMongoDbDocument

