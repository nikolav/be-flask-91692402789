

from config.graphql.init   import query
from models.assets         import Assets
from models.assets         import AssetsType
from models.assets         import AssetsStatus
from flask                 import g
from schemas.serialization import SchemaSerializeAssets
from flask_app             import TAG_ASSETS_SHAREABLE_GLOBALY


# assetsPostsReadable(uids: [ID!], pagination: JsonData, assets_rows: JsonData): [Asset!]!
@query.field('assetsPostsReadable')
def resolve_assetsPostsReadable(_obj, _info, uids = None, pagination = None, assets_rows = None):
  # pagination: {page:number, per_page:number}
  if None == uids:
    uids = [g.user.id]
  return SchemaSerializeAssets(many=True, exclude=('assets_has',)).dump(
      Assets.groups_related_assets_authored(*uids, 
        ASSETS_TYPES             = (AssetsType.DIGITAL_POST.value,),
        BLACKLIST_ASSET_STATUSES = (AssetsStatus.POSTS_BLOCKED.value,),
        WHITELIST_ASSET_TAGS     = (TAG_ASSETS_SHAREABLE_GLOBALY,),
        ORDERED                  = 'date_desc',
        PAGINATION               = pagination,
        ASSETS_ROWS              = assets_rows,
      ))


