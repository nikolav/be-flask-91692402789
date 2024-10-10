
from flask_app import db
from config.graphql.init import mutation

from models.assets import Assets

from schemas.validation.assets import SchemaInputAssets
from schemas.serialization     import SchemaSerializeAssets


# assetsUpdate(aid: ID!, fields: JsonData): JsonData!
@mutation.field('assetsUpdate')
def resolve_assetsUpdate(_obj, _info, aid, fields = None):

  r = { 'error': None, 'status': None }
  a = None

  try:

    data = SchemaInputAssets().load(fields) if None != fields else {}
    if not 0 < len(data):
      raise Exception('resolve_assetsUpdate --no-data')
      
    if not Assets.id_exists(aid):
      raise Exception('resolve_assetsUpdate --asset-not-found')
    
    a = db.session.get(Assets, aid)
    for field, value in data.items():
      if "data" != field:
        setattr(a, field, value)
      else:
        a.data_update(patch = value)
    
    db.session.commit()


  except Exception as err:
    r['error'] = str(err)


  else:
    if a:
      a.ioemit_update()
      r['status'] = { 'asset': SchemaSerializeAssets().dump(a) }


  return r

