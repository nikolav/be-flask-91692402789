
from config.graphql.init import query
from flask_app import mongo
from schemas.serialization import schemaSerializeMongoDocument
from src.classes import ResponseStatus
from schemas.validation.collections_config import SchemaValidateCollectionsConfig

from flask_pymongo import DESCENDING
from flask_pymongo import ASCENDING


SORT_STRATEGIES = {
  'date_desc': lambda q: q.sort('created_at', DESCENDING),
  'date_asc':  lambda q: q.sort('created_at', ASCENDING),
  '_default':  lambda q: q,
}

# collectionsByTopic(topic: String!, config: JsonData!): JsonData!
@query.field('collectionsByTopic')
def resolve_collectionsByTopic(_obj, _info, topic, config):
  # config: {fields: string[], sort: 'date_desc'|'date_asc' }
  r = ResponseStatus()

  try:
    config_ = SchemaValidateCollectionsConfig().load(config)
    sorted_ = SORT_STRATEGIES.get(config_.get('sort', '_default'))
    FIELDS = set(('_id',))
    FIELDS.update(config_['fields'])
    r.status = {
      'docs': schemaSerializeMongoDocument(FIELDS = tuple(FIELDS))(many = True).dump(
        sorted_(mongo.db[topic].find())),
    }
    
  except Exception as err:
    r.error = err


  return r.dump()

