
from config.graphql.init import query

from flask_app     import db
from models.users  import Users
from models.assets import Assets
from models.assets import AssetsType

from schemas.serialization import SchemaSerializeUsersTimes

# usersByGroups(gids: [ID!]!, ALL: Boolean): [User!]!
@query.field('usersByGroups')
def resolve_usersByGroups(_obj, _info, gids, ALL = False):
  # ALL: boolean; select user if belong to ALL provided groups

  # query.base, groups
  quids = db.select(
      Users.id
    ).distinct().join(
      Users.assets
    ).where(
      AssetsType.PEOPLE_GROUP_TEAM.value == Assets.type
    )
  
  if not ALL:
    # has any @gids
    quids = quids.where(
      Users.assets.any(
        Assets.id.in_(gids)
      )
    )
  
  else:
    # has all @gids
    for gid in set(gids):
      quids = quids.where(
        Users.assets.any(
          gid == Assets.id
        ))
  
  # sq_uids = quids.subquery()

  lsu = db.session.scalars(
    db.select(
      Users
    ).where(
      Users.id.in_(quids)
      # Users.id.in_(sq_uids)
    ))
  
  return SchemaSerializeUsersTimes(
      many    = True, 
      exclude = ('password',)
    ).dump(lsu)

