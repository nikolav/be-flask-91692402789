
from flask_app import db
from flask_app import io

from models.tags import Tags
from models.docs import Docs

from config.graphql.init import mutation

from . import IOEVENT_JsonData


@mutation.field('docsUpsert')
def resolve_docsUpsert(_obj, _info, topic, data, id = None):

  doc = None

  try:
    doc = db.session.scalar(
      db.select(
        Docs
      ).join(
        Docs.tags
      ).where(
        topic == Tags.tag, 
        id    == Docs.id))
  
    if doc:
      # update
      doc.data = data
      
    else:
      # create
      doc = Docs(data = data)
      tagTopic = Tags.by_name(topic, create = True)
      tagTopic.docs.append(doc)


    db.session.commit()


  except Exception as err:
    raise err

    
  else:
    io.emit(f'{IOEVENT_JsonData}{topic}')
  
      
  return doc.dump()
