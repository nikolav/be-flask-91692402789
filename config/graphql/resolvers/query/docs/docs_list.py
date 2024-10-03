from datetime import datetime
from datetime import timezone

from models.tags import Tags
from models.docs import Docs
from config.graphql.init import query

from schemas.serialization import SchemaSerializeDocJsonTimes



SORT_STRATEGIES = [
  # 0 created_at:asc
  { 'sort_key': lambda d: datetime.fromisoformat(d['created_at']), 'desc' : False },
  # 1 created_at:desc
  { 'sort_key': lambda d: datetime.fromisoformat(d['created_at']), 'desc' : True  },
]


@query.field('docsByTopic')
def resolve_docsByTopic(_obj, _info, topic, order = None):
  data = SchemaSerializeDocJsonTimes(many = True).dump(
    Tags.by_name(topic, create = True).docs)
  
  return sorted(data, 
                key     = SORT_STRATEGIES[order]['sort_key'],
                reverse = SORT_STRATEGIES[order]['desc']
              ) if None != order else data

