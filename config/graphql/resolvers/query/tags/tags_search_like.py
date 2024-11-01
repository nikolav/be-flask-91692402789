
from config.graphql.init import query
from models.tags import Tags
from flask_app import db
from flask_app import USERS_TAGS_prefix


# tagsSearchTagLike(search: String!, prefix: String, attach: String): [String!]!
@query.field('tagsSearchTagLike')
def resolve_tagsSearchTagLike(_obj, _info, search = '', prefix = '', attach = None):
  # attach = 'start' | 'end' | None
  search_ = (
      prefix + (
        ('%' + search) if search else ''
      )
    ) if prefix else search

  if 'start' == attach:
    search_ = search_ + '%'
  elif 'end' == attach:
    search_ = '%' + search_
  else:
    search_ = '%' + search_ + '%'
  
  ls = db.session.scalars(
    db.select(
      Tags
    ).where(
      Tags.tag.ilike(search_)
    ))
  

  return [t.tag for t in ls]

