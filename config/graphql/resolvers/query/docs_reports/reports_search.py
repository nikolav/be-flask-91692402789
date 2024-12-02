
from config.graphql.init import query
from flask_app import db

from models.docs import Docs
from models.docs import DocsTags
from models.tags import Tags

from schemas.serialization import SchemaSerializeDocs
from src.classes import ResponseStatus


queries_strategies = {
  'ids': lambda query_strategy_args: db.select(
      Docs
    ).where(
      Docs.id.in_(query_strategy_args)
    ),
  'ids:public': lambda query_strategy_args: db.select(
      Docs
    ).join(
      Docs.tags
    ).where(
      DocsTags.SHAREABLE.value == Tags.tag,
      Docs.id.in_(query_strategy_args)
    ),
}

# reportsSearch(query_strategy: String!, query_strategy_args: JsonData): JsonData!
@query.field('reportsSearch')
def resolve_reportsSearch(_obj, _info, query_strategy, query_strategy_args = None):
  r = ResponseStatus()

  try:
    dd = db.session.scalars(queries_strategies[query_strategy](query_strategy_args))
    r.status = { 'reports': SchemaSerializeDocs(many = True).dump(dd) }

  except Exception as err:
    r.error = err

  
  return r.dump()

