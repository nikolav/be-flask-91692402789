
from models.tags         import Tags
from models.docs         import Docs
from config.graphql.init import query

from schemas.serialization import SchemaSerializeDocJsonTimes

from flask_app import db

from fuzzywuzzy import fuzz
from fuzzywuzzy import process as fw_ps


# {[name:string]: strategy:def}
SEARCH_STRATEGIES_pre = {
  # identity,
  '_default': lambda q, args, *rest: q,
  # 'pre_name_startswith': lambda q, args, *rest: q.where(Docs.data['name'].startswith(args['q'].lower())),
}

DEFAULT_QSEARCH_LIMIT = 5
def resolve_qsearch_docs(ls_d, args, *rest):
  ls_d_ts  = { f'{d.serialize_to_qsearch()}': d for d in ls_d }
  matches = fw_ps.extract(args['q'].lower(), ls_d_ts.keys(),
                              limit  = args.get('limit', DEFAULT_QSEARCH_LIMIT),
                              scorer = fuzz.token_set_ratio,
                            )
  return [ls_d_ts[m[0]] for m in matches]

SEARCH_STRATEGIES_post = {
  # match q:string with @data.values:string
  'post_qstring': resolve_qsearch_docs,
}

SORT_STRATEGIES = [
  # 0 created_at:asc
  lambda q, args, *rest: q.order_by(Docs.created_at.asc()),
  # 1 created_at:desc
  lambda q, args, *rest: q.order_by(Docs.created_at.desc()),
  # 2 updated_at:asc
  lambda q, args, *rest: q.order_by(Docs.updated_at.asc()),
  # 3 updated_at:desc
  lambda q, args, *rest: q.order_by(Docs.updated_at.desc()),
]


# docsByTopic(topic: String!, order: Int, search: JsonData): [JsonData!]!
@query.field('docsByTopic')
def resolve_docsByTopic(_obj, _info, topic, order = None, search = {}):
  # search: { strategy:string; args?:{} }
  q    = None
  ls_d = None
  try:
    strategy_ = search.get('strategy')
    args_     = search.get('args', {})

    q = db.select(
      Docs
    ).join(
      Docs.tags
    ).where(
      topic == Tags.tag
    )
    
    if strategy_ and (strategy_ in SEARCH_STRATEGIES_pre):
      q = SEARCH_STRATEGIES_pre[strategy_](q, args_)
    
    if None != order:
      q = SORT_STRATEGIES[order](q, args_)
    
    ls_d = db.session.scalars(q)

    # apply _post query search strategy
    if strategy_ and (strategy_ in SEARCH_STRATEGIES_post):
      ls_d = SEARCH_STRATEGIES_post[strategy_](ls_d, args_)

      
  except Exception as err:
    raise err
  
    
  else:
    return SchemaSerializeDocJsonTimes(many = True).dump(ls_d)
  
  
  return []

