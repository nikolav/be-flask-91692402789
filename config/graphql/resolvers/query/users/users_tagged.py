
from config.graphql.init import query

from flask_app import db
from models.users import Users
from models.tags  import Tags
from schemas.serialization import SchemaSerializeUsersTimes

# usersTagged(tags: [String!]!, ALL: Boolean): [User!]!
@query.field('usersTagged')
def resolve_usersTagged(_obj, _info, tags, ALL = False):

  if 0 < len(tags):
    quids = None
    
    if not ALL:
      quids = db.select(
        Users.id
      ).distinct().join(
        Users.tags
      ).where(
        Users.tags.any(
          Tags.tag.in_(tags)
        )
      )
      # ).subquery()
      
    else:
      quids = db.select(
        Users.id
      ).distinct().join(
        Users.tags
      )
      
      for tag in set(tags):
        quids = quids.where(
          Users.tags.any(
            tag == Tags.tag
          )
        )
      
      # quids = quids.subquery()
    

    lsu = db.session.scalars(
      db.select(
        Users
      ).where(
        Users.id.in_(quids)
      )
    )
    
    return SchemaSerializeUsersTimes(
        many    = True, 
        exclude = ('password',)
      ).dump(lsu)
  
  return []