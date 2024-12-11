
from flask_app import db
from flask_app import TAG_USERS_EXTERNAL

from models.users import Users
from models.tags  import Tags

from config.graphql.init import query

from schemas.serialization import SchemaSerializeUsersTimes

from config import skip_list_users
from config import DEFAULT_GRAPHQL_USERS_LIST_SKIP_EXTERNAL


# users(skip_external: Boolean): [User!]!
@query.field('users')
def resolve_users(_obj, _info, skip_external = DEFAULT_GRAPHQL_USERS_LIST_SKIP_EXTERNAL):

  try:

    q = db.select(
        Users
      ).where(
        ~Users.id.in_(skip_list_users))

    if skip_external:
      q = q.where(
        ~Users.tags.any(
            TAG_USERS_EXTERNAL == Tags.tag))

    users = db.session.scalars(q)


    return SchemaSerializeUsersTimes(
      many    = True, 
      exclude = ('password',)).dump(users)


  except Exception as err:
    raise err


  return []
