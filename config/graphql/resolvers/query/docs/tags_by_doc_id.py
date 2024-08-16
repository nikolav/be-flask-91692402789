from flask_app           import db
from models.docs         import Docs
from config.graphql.init import query


@query.field('tagsByDocId')
def resolve_tagsByDocId(_obj, _info, id):
  try:
    return [t.tag for t in db.session.get(Docs, id).tags]
    
  except Exception as err:
    # print(err)
    raise err
    
  return []
