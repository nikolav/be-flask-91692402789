
from flask import g
from flask_app             import db
from config.graphql.init   import query
from models.assets         import Assets
from models.users          import Users
from schemas.serialization import SchemaSerializeAssets


# assetsList(aids: [ID!], type: String, own: Boolean): [Asset!]!
@query.field('assetsList')
def resolve_assetsList(_obj, _info, aids = None, type = None, own = True):

  q = db.select(
    Assets
  )
  
  # related assets only
  if own:
    q = q.join(
      Assets.users
    ).where(
      g.user.id == Users.id
    )

  if None != aids:
    q = q.where(
      Assets.id.in_(aids)
    )
  
  if None != type:
    q = q.where(
      type == Assets.type
    )
    
  lsa = db.session.scalars(q)

  return SchemaSerializeAssets(many = True).dump(lsa)

