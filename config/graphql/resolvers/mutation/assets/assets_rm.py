
from sqlalchemy import or_
from sqlalchemy import func

from config.graphql.init import mutation
from flask_app           import db
from flask_app           import io

from models.assets import Assets
from models.assets import AssetsIOEvents
from models        import ln_users_assets
from models        import ln_assets_tags
from models        import ln_assets_assets
from models.docs   import Docs

from middleware.authguard import authguard_assets_own
from flask_app            import POLICY_ADMINS
from src.classes.policies import Policies

from src.classes import ResponseStatus


# assetsRemove(aids: [ID!]!): JsonData!
@mutation.field('assetsRemove')
@authguard_assets_own(Policies.ASSETS_REMOVE.value, POLICY_ADMINS, ASSETS_OWN = "aids", ANY = True)
def resolve_assetsRemove(_obj, _info, aids):
  '''
    hard deletes assets and related records
  '''
  r = ResponseStatus()
  removed = False
  assets_selected = ()
  debug_assets_affected = ()

  try:
    assets_selected  = tuple(Assets.by_ids(*aids))
    assets_len_start = len(assets_selected)
    
    if 0 < assets_len_start:

      # rm --rel-tags
      db.session.execute(
        db.delete(
          ln_assets_tags
        ).where(
          ln_assets_tags.c.asset_id.in_(aids)))
      
      
      # rm --rel-users
      db.session.execute(
        db.delete(
          ln_users_assets
        ).where(
          ln_users_assets.c.asset_id.in_(aids)))
      
      
      # rm --rel-assets
      db.session.execute(
        db.delete(
          ln_assets_assets
        ).where(
          or_(
            ln_assets_assets.c.asset_r_id.in_(aids),
            ln_assets_assets.c.asset_l_id.in_(aids),
          )))
      
      # rm .asset_id fields @Docs
      db.session.execute(
        db.delete(
          Docs
        ).where(
          Docs.asset_id.in_(aids)
        ))
      
      debug_assets_affected = tuple({ 'id': a.id, 'type': a.type } for a in assets_selected)
      
      # rm --assets
      db.session.execute(
        db.delete(
          Assets
        ).where(
          Assets.id.in_(aids)))
      
      db.session.commit()

      # sanity check
      #  compare deleted ids .count with ..start
      removed = db.session.scalar(
        db.select(
          func.count(Assets.id)
        ).where(
          Assets.id.in_(aids)
        )) < assets_len_start

    r.status = { 'removed': removed }


  except Exception as err:
    r.error = err
  
  
  else:
    if removed:
      # emit asset:removed:ID
      # emit asset:type

      for a in debug_assets_affected:
        io.emit(f'{AssetsIOEvents.REMOVE.value}:{a['id']}')

      for a_type in set(map(lambda a: a['type'], debug_assets_affected)):
        if a_type:
          io.emit(a_type)


  return r.dump()

