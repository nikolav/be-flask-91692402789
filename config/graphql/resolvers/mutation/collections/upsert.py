
from config.graphql.init import mutation
from src.classes import ResponseStatus
from flask_app import mongo
from flask_app import io
from schemas.serialization import schemaSerializeMongoDocument
from datetime import datetime
from datetime import timezone
from bson import ObjectId
from flask_app import IOEVENT_COLLECTIONS_UPSERT_prefix

# collectionsUpsert(topic: String!, data: JsonData!, fields: [String!]!, id: ID): JsonData!
@mutation.field('collectionsUpsert')
def resolve_collectionsUpsert(_obj, _info, topic, data, fields, id = None):
  r = ResponseStatus()
  d = None
  id_affected = id
  

  try:
    NOW = datetime.now(tz = timezone.utc)
    
    if None != id:
      d = mongo.db[topic].find_one({'_id': ObjectId(id)})

    if None != d:
      # @update
      data.update({'updated_at': NOW})
      mongo.db[topic].update_one({'_id': ObjectId(id)}, {'$set': data})
    else:
      # @add
      data.update({'created_at': NOW, 'updated_at': NOW})
      res = mongo.db[topic].insert_one(data)
      id_affected = res.inserted_id
  
  except Exception as err:
    r.error = err
  
  else:
    FIELDS = set(('_id',))
    FIELDS.update(fields)
    r.status = { 
      'doc': schemaSerializeMongoDocument(FIELDS = tuple(FIELDS))().dump(
        mongo.db[topic].find_one({'_id': ObjectId(id_affected)})),
    }
    io.emit(f'{IOEVENT_COLLECTIONS_UPSERT_prefix}{topic}')


  return r.dump()

