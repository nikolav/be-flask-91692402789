
from sqlalchemy import or_
from sqlalchemy import func

from config.graphql.init import mutation
from flask_app           import db
from flask_app           import io

from models.assets import Assets
from models        import ln_users_assets
from models        import ln_assets_tags
from models        import ln_assets_assets


@mutation.field('assetsRemove')
def resolve_assetsRemove(_obj, _info, aids):
  r = { 'error': None, 'status': None }
  removed = False
  assets_affected = ()

  try:
    assets_affected        = tuple(Assets.by_ids(*aids))
    assets_len_start       = len(assets_affected)
    assets_affected_types  = set(map(lambda a: a.type, assets_affected))
    
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

    r['status'] = { 'removed': removed }


  except Exception as err:
    r['error'] = str(err)
  
  
  else:
    if removed:
      for a_type in assets_affected_types:
        if a_type:
          io.emit(a_type)


  return r

