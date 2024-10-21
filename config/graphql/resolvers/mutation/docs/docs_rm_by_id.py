
from flask_app import db
from flask_app import io

from models.docs import Docs

from config.graphql.init import mutation

from . import IOEVENT_JsonData


@mutation.field('docsRmById')
def resolve_docsRmById(_obj, _info, id):
  '''
  remove/unlink doc by ID;
  notify topics
  '''

  doc    = None
  topics = []

  try:
    doc = db.session.get(Docs, id)
    
    if doc:
      for tag_ in doc.tags:
        tag_.docs.remove(doc)
        topics.append(tag_.tag)

      db.session.delete(doc)
      db.session.commit()


  except Exception as e:
    raise e
    # pass
  
  else:
    if doc:
      for topic in topics:
        io.emit(f'{IOEVENT_JsonData}{topic}')
      return doc.dump()
  

  return None

