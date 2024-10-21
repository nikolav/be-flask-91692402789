
from flask_app import db
from flask_app import io

from models.tags import Tags
from models.docs import Docs

from config.graphql.init import mutation

from . import IOEVENT_JsonData


@mutation.field('docsRm')
def resolve_docsRm(_obj, _info, topic, id):
  '''
  remove/unlink doc by 'ID' in 'topic';
  notify related topics
  '''

  d      = None
  topics = set()

  try:
    d = db.session.scalar(
      db.select(
        Docs
      ).join(
        Docs.tags
      ).where(
        Docs.tags.any(
          topic == Tags.tag
        ),
        id == Docs.id
      ))

    if d:
      for t in d.tags:
        t.docs.remove(d)
        topics.add(t.tag)

      db.session.delete(d)
      db.session.commit()


  except:
    pass
  

  else:
    if d:
      for topic in topics:
        io.emit(f'{IOEVENT_JsonData}{topic}')
      
      return d.dump()
  
  
  return None

