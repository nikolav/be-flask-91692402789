
from config.graphql.init import query

from models.users import Users

from fuzzywuzzy import fuzz
from fuzzywuzzy import process

from schemas.serialization import SchemaSerializeUsersTimes


# usersQ(q: String!, limit: Int): [User!]!
@query.field('usersQ')
def resolve_usersQ(_obj, _info, q, limit = 5):
  lsu     = Users.list_all_safe()
  lsu_ts  = { f'{u.serialize_to_text_search()}': u for u in lsu }
  matches = process.extract(q.lower(), lsu_ts.keys(),
                              limit  = limit,
                              scorer = fuzz.token_set_ratio
                            )

  return SchemaSerializeUsersTimes(
      many    = True, 
      exclude = ('password',)
    ).dump(
      [lsu_ts[m[0]] for m in matches]
    )

