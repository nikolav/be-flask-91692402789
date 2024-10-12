
from flask_app             import db
from config.graphql.init   import query
from models.assets         import Assets
from schemas.serialization import SchemaSerializeAssets


# assetsList(aids: [ID!], type: String): [Asset!]!
@query.field('assetsList')
def resolve_assetsList(_obj, _info, aids = None, type = None):
  q = db.select(
    Assets)

  if None != aids:
    q = q.where(
      Assets.id.in_(aids))
  
  if None != type:
    q = q.where(
      type == Assets.type)
  
  lsa = db.session.scalars(q)

  return SchemaSerializeAssets(many = True).dump(lsa)

