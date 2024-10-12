
from flask import g

from config.graphql.init import mutation

from flask_app     import db
from flask_app     import io

from models.assets import Assets

from schemas.validation.assets import SchemaInputAssets
from schemas.validation.assets import SchemaInputAssetsCreate
from schemas.serialization     import SchemaSerializeAssets


# assetsUpsert(fields: JsonData!, aid: ID): JsonData!
@mutation.field('assetsUpsert')
def resolve_assetsUpsert(_obj, _info, fields = {}, aid = None):
  a = None
  d = None
  r = { 'error': None, 'status': None }
  
  created = False
  
  
  try:
    d = SchemaInputAssets().load(fields)
    if not 0 < len(d):
      raise Exception('resolve_assetsUpsert --no-data')
    
    if None != aid:
      # raise|update
      
      a = db.session.get(Assets, aid)
      if not a:
        raise Exception('resolve_assetsUpsert --no-asset')
      
      for field, value in d.items():
        if "data" != field:
          setattr(a, field, value)
        else:
          a.data_update(patch = value)
      
    else:
      # create
      
      a = Assets(
        **SchemaInputAssetsCreate().load(d),
        author = g.user
      )
      db.session.add(a)
      created = True
    
    db.session.commit()

    
  except Exception as err:
    r['error'] = str(err)

  
  else:
    if a:
      r['status'] = { 'asset': SchemaSerializeAssets(exclude = ('assets_has',)).dump(a) }
      io.emit(a.type)
      if not created:
        a.ioemit_update()
  
  
  return r

