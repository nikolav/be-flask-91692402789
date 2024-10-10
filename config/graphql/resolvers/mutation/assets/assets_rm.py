
from sqlalchemy import or_
from sqlalchemy import func

from config.graphql.init import mutation
from flask_app           import db

from models.assets import Assets
from models        import ln_users_assets
from models        import ln_assets_tags
from models        import ln_assets_assets


@mutation.field('assetsRemove')
def resolve_assetsRemove(_obj, _info, aids):
  r = { 'error': None, 'status': None }
  any_assets_removed = False

  try:

    assets_len_start = db.session.scalar(
      db.select(
        func.count(Assets.id)
      ).where(
        Assets.id.in_(aids)
      ))
    
    
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
      any_assets_removed = db.session.scalar(
        db.select(
          func.count(Assets.id)
        ).where(
          Assets.id.in_(aids)
        )) < assets_len_start

    r['status'] = { 'any_assets_removed': any_assets_removed }


  except Exception as err:
    r['error'] = str(err)
  
  
  else:
    if any_assets_removed:
      Assets.ioemit_groups_change()


  return r


