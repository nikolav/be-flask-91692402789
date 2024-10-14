from copy import deepcopy

from flask_app import db
from flask_app import io

from models.docs import Docs
from config.graphql.init import mutation
from . import IOEVENT_DOC_CHANGE_prefix

from utils.merge_strategies import dict_deepmerger_extend_lists as merger


@mutation.field('docUpsert')
def resolve_docUpsert(_obj, _info, doc_id, data, merge = True, shallow = False):
  # docUpsert(doc_id: String!, data: JsonData!, merge: Boolean!, shallow: Boolean!): JsonData!
  d   = data
  doc = Docs.by_doc_id(doc_id, create = True)
  try:
    if merge:
      if shallow:
        d = doc.data.copy()
        d.update(data)
      else:
        d = merger.merge(deepcopy(doc.data), data)
    
    doc.data = d
    db.session.commit()

  except Exception as err:
    raise err

  else:
    # emit updated
    io.emit(f'{IOEVENT_DOC_CHANGE_prefix}{doc_id}')
  
  return doc.dump()
