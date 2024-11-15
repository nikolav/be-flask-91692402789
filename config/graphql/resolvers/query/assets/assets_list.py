
from flask import g
from flask_app             import db
from config.graphql.init   import query
from models.assets         import Assets
from models.assets         import AssetsType
from models.users          import Users
from schemas.serialization import SchemaSerializeAssets


# assetsList(aids: [ID!], type: String, own: Boolean, aids_subs_only: [ID!], aids_subs_type: String): [Asset!]!
@query.field('assetsList')
def resolve_assetsList(_obj, _info, 
                       aids           = None, 
                       type           = None, 
                       own            = True, 
                       aids_subs_only = None, 
                       aids_subs_type = None,
                      ):

  q   = None
  lsa = None
  
  if AssetsType.PHYSICAL_STORE.value == type:

    if True == own:
      if aids_subs_only:
        # fetch some managed sites
        #   only provided groups: @aids_subs_only?: number[]
        lsa = Assets.assets_parents(
            *Assets.by_ids_and_type(*aids_subs_only, type = aids_subs_type),
            PtAIDS   = aids,
            TYPE     = type,
            WITH_OWN = False,
          )
      else:
        # fetch *managed sites
        lsa = g.user.related_assets_sites_managed(
            PtAIDS   = aids, 
            WITH_OWN = False,
          )

    else:
      # fetch all sites
      q = db.select(
          Assets
        ).where(
          AssetsType.PHYSICAL_STORE.value == Assets.type)
      # only @IDs
      if aids:
        q = q.where(
          Assets.id.in_(aids))
      
      lsa = db.session.scalars(q)
      

  else:
    
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
  
    
  return SchemaSerializeAssets(
      many    = True,
      exclude = ('assets_has',)
    ).dump(lsa)

