
from flask import g

from flask_app           import db
from config.graphql.init import mutation

from models.assets import Assets
from models.assets import AssetsType

from schemas.serialization     import SchemaSerializeAssets
from schemas.validation.assets import SchemaInputAssetsAdd


@mutation.field('groupsAdd')
def resolve_groupsAdd(_obj, _info, name, fields = {}):
  a = None
  try:
    a = Assets(
      **(SchemaInputAssetsAdd().load(fields) if fields != None else {}),
      type   = AssetsType.PEOPLE_GROUP_TEAM.value,
      name   = name,
      author = g.user,
    )
    db.session.add(a)
    db.session.commit()
    

  except Exception as err:
    raise err
  
  
  else:
    if None != a:
      Assets.ioemit_groups_change()
      return SchemaSerializeAssets().dump(a)
    

  return None

