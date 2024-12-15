
from config.graphql.init import mutation
from src.classes import ResponseStatus

from flask_app import db
from models.assets import Assets
from models.assets import AssetsType
from models.docs   import Docs

from flask_app     import io
from models.assets import AssetsIOEvents

from schemas.serialization import SchemaSerializeDocs

from flask import g


# assetsFormsSubmission(data: JsonData!, fid: ID!, key: String): JsonData!
@mutation.field('assetsFormsSubmission')
def resolve_assetsFormsSubmission(_obj, _info, data, fid, key = None):
  r = ResponseStatus()
  a = None
  
  dd_form_submission = None


  try:
    a = db.session.scalar(
      db.select(
        Assets
      ).where(
        AssetsType.DIGITAL_FORM.value == Assets.type,
        fid == Assets.id
      ))
    
    if not a:
      raise Exception('assetsFormsSubmission --no-asset-found')
    
    dd_form_submission = Docs(
      key  = key,
      data = data,
    )

    dd_form_submission.user = g.user
    
    db.session.add(dd_form_submission)
    a.docs.append(dd_form_submission)

    db.session.commit()

  
  except Exception as err:
    raise err

    
  else:
    # r.status = { 'key': dd_form_submission.key }
    r.status = { 'submission': SchemaSerializeDocs(only = ('id', 'key',)).dump(dd_form_submission) }
    io.emit(f'{AssetsIOEvents.IOEVENT_ASSETS_FORMS_SUBMISSION_prefix.value}{a.key}')
  
  
  return r.dump()



