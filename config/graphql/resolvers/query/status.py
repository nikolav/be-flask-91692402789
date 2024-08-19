from config.graphql.init import query


@query.field('status')
def resolve_status(_o, _i):
  return 'ok'
