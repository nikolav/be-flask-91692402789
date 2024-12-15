
from config.graphql.init import query

from flask import g

from flask_app import db

from models.assets import Assets
from models.users  import Users
from models.assets import AssetsType

from schemas.serialization import SchemaSerializeUsersTimes

# usersSharedGroups(uids: [ID!]): [User!]!
@query.field('usersSharedGroups')
def resolve_usersSharedGroups(_obj, _info, uids = None):

  if None == uids:
    uids = [g.user.id]

  if 0 < len(uids):
    sq_groups_lookup = db.select(
      Assets.id
    ).join(
      Assets.users
    ).where(
      AssetsType.PEOPLE_GROUP_TEAM.value == Assets.type,
      Users.id.in_(uids)
    )
    # ).subquery()

    quids = db.select(
      Users.id
    ).distinct().join(
      Users.assets
    ).where(
      Assets.id.in_(sq_groups_lookup)
    )
    # ).subquery()

    qu = db.select(
      Users
    ).where(
      Users.id.in_(quids))
    
    lsu = db.session.scalars(qu)
    return SchemaSerializeUsersTimes(
        many    = True, 
        exclude = ('password',)
      ).dump(lsu)
  
  return []


