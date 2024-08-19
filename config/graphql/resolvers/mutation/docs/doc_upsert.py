from flask_app import db
from flask_app import io

from models.docs import Docs
from config.graphql.init import mutation
from . import IOEVENT_DOC_CHANGE_prefix


@mutation.field('docUpsert')
def resolve_docUpsert(_obj, _info, doc_id, data, merge = True):
  # docUpsert(doc_id: String!, data: JsonData!, merge: Boolean!): JsonData!
  doc = Docs.by_doc_id(doc_id, create = True)

  try:
    # doc.data = data
    if merge:
      d = doc.data.copy()
      d.update(data)
    else:
      d = data
    
    doc.data = d
    db.session.commit()

  except:
    pass

  else:
    # emit updated
    io.emit(f'{IOEVENT_DOC_CHANGE_prefix}{doc_id}')
  
  return doc.dump()
