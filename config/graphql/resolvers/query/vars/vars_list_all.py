from config.graphql.init import query
from models.docs         import Docs


@query.field('vars')
def resolve_vars(_o, _i):
  return Docs.vars_list()
