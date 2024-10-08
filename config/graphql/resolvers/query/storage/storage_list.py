from flask import g

from config.graphql.init import query
from models.docs         import Docs


@query.field('storageList')
def resolve_storageList(obj, info):
  return (doc.get_data({
      'id': doc.id,
      'created_at': str(doc.created_at),
      'updated_at': str(doc.updated_at),
    }) for doc in Docs.storage_ls(g.user.id))
