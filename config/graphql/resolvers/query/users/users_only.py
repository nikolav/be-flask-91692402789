
from flask_app             import db
from config.graphql.init   import query
from models.users          import Users
from schemas.serialization import SchemaSerializeUsersTimes


@query.field('usersOnly')
def resolve_usersOnly(_obj, _info, uids):
  if 0 < len(uids):
    try:
      return SchemaSerializeUsersTimes(many = True, exclude = ('password',)).dump(      
        db.session.scalars(
          db.select(
            Users
          ).where(
            Users.id.in_(uids)
          )
        )
      )
    except Exception as err:
      raise err
  
  return []
