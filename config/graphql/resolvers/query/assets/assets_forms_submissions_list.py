
from config.graphql.init import query

from flask import g
from models.assets import Assets
from models.assets import AssetsType
from models.docs   import Docs

from flask_app import db
from schemas.serialization import SchemaSerializeDocs

from utils.dates import week_start
from utils.dates import month_start

from datetime import datetime
from datetime import timedelta
from datetime import timezone


FILTERS_DATETIME = {

  # # older than..
  # 'older-than': lambda qd, dd: qd.where(
  #     Docs.created_at <= datetime.fromisoformat(dd)
  #   ),

  # # newer than..
  # 'newer-than': lambda qd, dd: qd.where(
  #     datetime.fromisoformat(dd) <= Docs.created_at
  #   ),

  # from.. to..
  'date-range': lambda qd, dfrom, dto: qd.where(
      datetime.fromtimestamp(dfrom) <= Docs.created_at,
      Docs.created_at <= datetime.fromtimestamp(dto),
    ),
  
  # this month
  'month': lambda qd, *args: qd.where(
      month_start() <= Docs.created_at
    ),

  # 
  'previous-week': lambda qd, *args: qd.where(
    week_start() - timedelta(days = 7) <= Docs.created_at,
    Docs.created_at <= week_start(),
  ),

  # 
  'today': lambda qd, *args: qd.where(
      datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) <= Docs.created_at,
    ),
  
  # @this-week
  '_default': lambda qd, *args: qd.where(
      week_start() < Docs.created_at
    ),
}

# assetsFormsSubmissionsList(strategy: String): [Docs!]!
@query.field('assetsFormsSubmissionsList')
def resolve_assetsFormsSubmissionsList(_obj, _info, strategy = '_default', args = []):
  # get @forms
  #  select docs where docs.asset_id in @forms
  #   order date.desc
  forms = Assets.assets_parents(

      # parent groups
      *g.user.groups(),
      
      # get forms
      TYPE = AssetsType.DIGITAL_FORM.value,
      
      # no own assets
      WITH_OWN = False,
    )
  fids = map(lambda a: a.id, forms)

  qd = db.select(
      Docs
    ).where(
      Docs.asset_id.in_(fids)
    )
  
  qd = FILTERS_DATETIME[strategy](qd, *args)
    
  qd = qd.order_by(
      Docs.updated_at.desc()
    )

  lsd = db.session.scalars(qd)
  

  return SchemaSerializeDocs(many = True).dump(lsd)
  
