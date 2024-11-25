
from config.graphql.init import mutation
from src.classes         import ResponseStatus

from flask_app     import db
from flask_app     import io
from models.assets import Assets
from models.assets import AssetsIOEvents


# assetsPatchData(aid: ID!, patch: JsonData!): JsonData!
@mutation.field('assetsPatchData')
def resolve_assetsPatchData(_obj, _info, aid, patch):
  r = ResponseStatus()

  try:
    a = db.session.get(Assets, aid)
    if not a:
      raise Exception('assets:patch:invalid-input')
    if 0 == len(patch):
      raise Exception('assets:patch:invalid-data')
    
    a.data_update(patch = patch)
    db.session.commit()
    
  except Exception as err:
    r.error = err
  
  else:
    r.status = { 'data': a.data }
    io.emit(f'{AssetsIOEvents.UPDATE.value}{a.id}')


  return r.dump()

