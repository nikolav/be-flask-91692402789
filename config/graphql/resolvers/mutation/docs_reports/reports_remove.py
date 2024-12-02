
from config.graphql.init import mutation
from src.classes import ResponseStatus

from flask_app   import db
from models.docs import Docs
from models      import ln_docs_tags

from middleware.authguard import authguard_reports_manage

from flask_app            import POLICY_ADMINS
from src.classes.policies import Policies


# reportsDrop(ids: [ID!]!): JsonData!
@mutation.field('reportsDrop')
@authguard_reports_manage(POLICY_ADMINS, Policies.REPORTS_MANAGE.value, REPORTS_KEY = "ids")
def resolve_reportsDrop(_obj, _info, ids):
  r = ResponseStatus()
  ls_ids_rm = []

  try:
    
    ls_ids_rm = list(db.session.scalars(
      db.select(
        Docs.id
      ).where(
        Docs.id.in_(ids)
      )))
    

    if 0 < len(ls_ids_rm):    
      
      db.session.execute(
        db.delete(
          ln_docs_tags
        ).where(
          ln_docs_tags.c.doc_id.in_(ls_ids_rm)
        ))

      db.session.execute(
        db.delete(
          Docs
        ).where(
          Docs.id.in_(ls_ids_rm)
        ))

      db.session.commit()
    
    r.status = { 'removed': ls_ids_rm }
  
  
  except Exception as err:
    r.error = err


  return r.dump()



  