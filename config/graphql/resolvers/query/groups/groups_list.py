
from config.graphql.init   import query
from models.assets         import Assets
from schemas.serialization import SchemaSerializeAssets

@query.field('groupsList')
def resolve_groupsList(_obj, _inf, gids = None):
  lsg = Assets.groups_all() if None == gids else Assets.groups_only(gids)
  return SchemaSerializeAssets(
      many    = True, 
      exclude = ('assets_has',)
    ).dump(lsg)
