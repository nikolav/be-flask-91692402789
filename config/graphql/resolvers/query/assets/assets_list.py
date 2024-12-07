
from flask import g
from flask_app             import db
from config.graphql.init   import query
from models.assets         import Assets
from models.assets         import AssetsType
from models.assets         import AssetsStatus
from models.users          import Users
from schemas.serialization import SchemaSerializeAssets

ASSETS_WITH_GROUPS_RELATIONS = (
  AssetsType.PHYSICAL_STORE.value,
  AssetsType.DIGITAL_CHAT.value,
  AssetsType.DIGITAL_FORM.value,
  AssetsType.DIGITAL_POST.value,
)

STRATEGY_order = {
  'date_asc'  : lambda lsa: sorted(lsa, key = lambda a: a.created_at),
  'date_desc' : lambda lsa: sorted(lsa, key = lambda a: a.created_at, reverse = True),
}

# assetsList(aids: [ID!], type: String, own: Boolean, aids_subs_only: [ID!], aids_subs_type: String, children: Boolean, category: String, my_only: Boolean, ordered: String): [Asset!]!
@query.field('assetsList')
def resolve_assetsList(_obj, _info, 
                       aids           = None, 
                       type           = None, 
                       own            = True, 
                       aids_subs_only = None, 
                       aids_subs_type = None,
                       children       = False,
                       category       = None,
                       my_only        = False,
                       ordered        = None,
                      ):
  
  q   = None
  lsa = None
  
  
  if True == children:
    # search child nodes
    #  site => groups
    #  form => groups
    #  chat => groups
    #  post => groups
    lsa = Assets.assets_children(*Assets.by_ids(*aids), TYPE = type)
  

  elif type in ASSETS_WITH_GROUPS_RELATIONS:
    # search self:relations/asset-asset for this types
    #  groups-sites
    #  groups-forms
    #  groups-chats
    #  groups-posts

    if True == own:
      if aids_subs_only:
        # fetch some managed parent assets
        #   only related to provided groups: @aids_subs_only?: number[]
        lsa = Assets.assets_parents(
            *Assets.by_ids_and_type(*aids_subs_only, type = aids_subs_type),
            PtAIDS   = aids,
            TYPE     = type,
            WITH_OWN = False,
          )
      else:
        # fetch *related assets:parents
        lsa = g.user.related_assets(
            TYPE     = type,
            PtAIDS   = aids, 
            WITH_OWN = False,
          )

    else:
      # fetch all assets
      q = db.select(
          Assets
        ).where(
          type == Assets.type)
      
      # only @IDs
      if aids:
        q = q.where(
          Assets.id.in_(aids))
    
      # only for this user
      if True == my_only:
        q = q.where(
          g.user.id == Assets.author_id)
      
      lsa = db.session.scalars(q)
      

  else:
    # query user groups

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
  
  if None != category:
    lsa = filter(lambda a: category == a.category_key(), lsa)

  if None != ordered and ordered in STRATEGY_order:
    lsa = STRATEGY_order[ordered](lsa)
    
  return SchemaSerializeAssets(
      many    = True,
      exclude = ('assets_has',)
    ).dump(lsa)

