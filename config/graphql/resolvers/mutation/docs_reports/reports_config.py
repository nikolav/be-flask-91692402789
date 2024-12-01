
from config.graphql.init import mutation
from src.classes import ResponseStatus
from middleware.authguard import authguard_reports_manage
from src.classes.policies import Policies
from flask_app import POLICY_ADMINS
from models.docs import Docs
from models.tags import Tags
from flask_app import db


# reportsConfigurationTags(ids: [ID!]!, config: JsonData!): JsonData!
@mutation.field('reportsConfigurationTags')
@authguard_reports_manage(POLICY_ADMINS, Policies.REPORTS_MANAGE.value, 
                          REPORTS_KEY = 'ids', ANY = True)
def resolve_reportsConfigurationTags(_obj, _info, ids, config):
  # config: { tags:any }
  r = ResponseStatus()

  try:
    setup_tags = config.get('tags', {})
    if setup_tags:
      lsr = Docs.by_ids(*ids)
      for tname, tval in setup_tags.items():
        t = Tags.by_name(tname, create = True, _commit = False)
        if tval:
          for dr in filter(lambda d: not d in t.docs, lsr):
            t.docs.append(dr)
        else:
          for dr in filter(lambda d: d in t.docs, lsr):
            t.docs.remove(dr)
    
      db.session.commit()


  except Exception as err:
    r.error = err
  
  
  else:
    r.status = 'ok'


  return r.dump()



  