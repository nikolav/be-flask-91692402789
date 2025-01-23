
from config.graphql.init import query
from flask_app import mongo
from schemas.serialization import schemaSerializeMongoDocument
from src.classes import ResponseStatus
from schemas.validation.collections_config import SchemaValidateCollectionsConfig


# collectionsByTopic(topic: String!, config: JsonData!): JsonData!
@query.field('collectionsByTopic')
def resolve_collectionsByTopic(_obj, _info, topic, config):
  r = ResponseStatus()

  try:
    FIELDS = set(('_id',))
    FIELDS.update(SchemaValidateCollectionsConfig().load(config)['fields'])
    r.status = {
      'docs': schemaSerializeMongoDocument(FIELDS = tuple(FIELDS))(many = True).dump(mongo.db[topic].find({})),
    }
    
  except Exception as err:
    r.error = err

  return r.dump()


