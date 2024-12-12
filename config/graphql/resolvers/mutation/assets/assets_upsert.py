
from flask import g

from config.graphql.init import mutation

from flask_app     import db
from flask_app     import io

from models.assets import Assets
from models.assets import AssetsType
from models.assets import AssetsStatus

# from schemas.validation.assets import SchemaInputAssets
from schemas.validation.assets import SchemaInputAssetsCreate
from schemas.serialization     import SchemaSerializeAssets

from src.classes import ResponseStatus


# assetsUpsert(fields: JsonData!, aid: ID, merge_field_data: Boolean): JsonData!
@mutation.field('assetsUpsert')
def resolve_assetsUpsert(_obj, _info, fields = {}, aid = None, merge_field_data = True):
  # fields: { ...cols, category:string }
  a = None
  d = None
  r = ResponseStatus()
  
  created = False
  
  
  try:
    
    if None != aid:
      # raise|update

      d = SchemaInputAssetsCreate(
          partial = ('name',), 
          #  skip updates @.type field
          exclude = ('type',)
        ).load(fields)
      
      if not 0 < len(d):
        raise Exception('resolve_assetsUpsert --no-data')
      
      a = db.session.get(Assets, aid)
      if not a:
        raise Exception('resolve_assetsUpsert --no-asset')
            

      for field, value in d.items():
        if 'category' != field:
          if 'data' != field:
            setattr(a, field, value)
          else:
            a.data_update(patch = value, merge = True == merge_field_data)
        else:
          a.category_key_commit(value, _commit = False)
      
    else:
      # create
      
      a = Assets(
        **SchemaInputAssetsCreate(
            exclude = ('category',)
          ).load(fields),
        author = g.user,
        # users  = [g.user],
      )

      if a.type in (
        AssetsType.PEOPLE_GROUP_TEAM.value,
      ):
        # include author in new asset:group
        a.users = [g.user]

      a.category_key_commit(fields.get('category'), _commit = False)

      # author access @init
      if a.type in (
        AssetsType.DIGITAL_POST.value,
      ):
        a.status = AssetsStatus.POSTS_BLOCKED.value

      
      db.session.add(a)
      created = True
    
    db.session.commit()

    
  except Exception as err:
    r.error = err

  
  else:
    if a:
      r.status = { 
        'created' : created, 
        'asset'   : SchemaSerializeAssets(exclude = ('assets_has', 'users',)).dump(a),
      }
      io.emit(a.type)
      if not created:
        a.ioemit_update()
  
  
  return r.dump()

