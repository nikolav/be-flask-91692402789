
from config.graphql.init import mutation
from src.classes import ResponseStatus
from flask_app import mongo
from flask_app import io
from flask_app import IOEVENT_COLLECTIONS_UPSERT_prefix
from bson import ObjectId

# collectionsDrop(topic: String!, ids: [ID!]): JsonData!
@mutation.field('collectionsDrop')
def resolve_collectionsDrop(_obj, _info, topic, ids = None):
  r = ResponseStatus()
  deleted_count = 0


  try:
    if ids:
      res = mongo.db[topic].delete_many({'_id': {'$in': [ObjectId(id) for id in set(ids)]}})
      deleted_count = res.deleted_count
    
  except Exception as err:
    r.error = err
  
  else:
    r.status = {
      'deleted_count': deleted_count,
    }
    if 0 < deleted_count:
      io.emit(f'{IOEVENT_COLLECTIONS_UPSERT_prefix}{topic}')


  return r.dump()


