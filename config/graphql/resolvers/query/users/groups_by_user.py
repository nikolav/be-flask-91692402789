
from config.graphql.init import query
from flask_app import db
from models.users import Users
from schemas.serialization import SchemaSerializeAssets


# groupsByUser(uid: ID!): [Asset!]!
@query.field('groupsByUser')
def resolve_groupsByUser(_obj, _info, uid):
  
  try:
    u = db.session.get(Users, uid)
    if u:
      return SchemaSerializeAssets(
          many    = True, 
          exclude = ('assets_has', 'users', ),
        ).dump(
          u.groups())
  
  
  except Exception as err:
    raise err
  
  
  return []

