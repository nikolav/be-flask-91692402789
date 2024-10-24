from flask_app import db

from models.users import Users

from config.graphql.init import query

from schemas.serialization import SchemaSerializeUsersTimes

from config import skip_list_users


@query.field('users')
def resolve_users(_obj, _info):

  try:
    users = db.session.scalars(
      db.select(
        Users
      ).where(
        ~Users.id.in_(skip_list_users)
      )
    )
    return SchemaSerializeUsersTimes(
      many    = True, 
      exclude = ('password', 'products', 'posts',)).dump(users)

  except Exception as err:
    raise err

  return []
