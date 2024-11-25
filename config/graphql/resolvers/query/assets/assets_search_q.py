
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

from config.graphql.init import query

from flask_app import db
from models.assets import Assets
from schemas.serialization import SchemaSerializeAssets

# assetsSearchQ(q: String!, type: String, limit: Int): [Asset!]!
@query.field('assetsSearchQ')
def resolve_assetsSearchQ(_obj, _info, q, type = None, limit = 10):

  qa = db.select(Assets)
  if type:
    qa = qa.where(type == Assets.type)
  
  lsa     = db.session.scalars(qa)
  lsa_ts  = { f'{a.serialize_to_text_search()}': a for a in lsa }
  matches = process.extract(q.lower(), lsa_ts.keys(),
                              limit  = limit,
                              scorer = fuzz.token_set_ratio,
                            )

  return SchemaSerializeAssets(
      many    = True, 
      exclude = ('assets_has',)
    ).dump(
      [lsa_ts[m[0]] for m in matches]
    )
