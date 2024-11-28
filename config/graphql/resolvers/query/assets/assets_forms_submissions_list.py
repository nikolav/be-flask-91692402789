
from config.graphql.init import query

from flask import g
from models.assets import Assets
from models.assets import AssetsType
from models.docs   import Docs

from flask_app import db
from schemas.serialization import SchemaSerializeDocs


# assetsFormsSubmissionsList: [Docs!]!
@query.field('assetsFormsSubmissionsList')
def resolve_assetsFormsSubmissionsList(_obj, _info):
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

  lsd = db.session.scalars(
    db.select(
      Docs
    ).where(
      Docs.asset_id.in_(fids)
    ).order_by(
      Docs.updated_at.desc()))

  return SchemaSerializeDocs(many = True).dump(lsd)
  
