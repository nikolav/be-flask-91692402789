from config.graphql.init import query


@query.field('status')
def status(_o, _i):
  return 'ok'
