from functools import wraps

from flask import g
from flask import abort
from flask import make_response

from models.assets import Assets
from models.docs   import Docs


# assert: --policies
def authguard(*policies, ANY = False):
  def with_authguard(fn_route):
    @wraps(fn_route)
    def wrapper(*args, **kwargs):
      if not g.user.includes_tags(*policies, ANY = ANY):
        return abort(make_response('', 403))
      return fn_route(*args, **kwargs)
    return wrapper
  return with_authguard

# assert: --policies-pass; owns* assets@kwargs.aids
def authguard_assets_own(*policies, ASSETS_OWN = None, ANY = False):
  def with_authguard_assets_own(fn_route):
    @wraps(fn_route)
    def wrapper(*args, **kwargs):
      # passes if 
      #  has policies
      #  author of related assets
      if not (g.user.includes_tags(
        *policies, ANY = ANY
      ) or (ASSETS_OWN and all(
        a.author.id == g.user.id for a in Assets.by_ids(*kwargs.get(ASSETS_OWN, []))
      ))):
        return abort(make_response('', 403))
      return fn_route(*args, **kwargs)
    return wrapper
  return with_authguard_assets_own


# reports:manage --has-policies --owns
def authguard_reports_manage(*policies, REPORTS_KEY = "ids", ANY = True):
  def with_authguard_reports_manage(fn_route):
    @wraps(fn_route)
    def wrapper(*args, **kwargs):
      if not (g.user.includes_tags(
        *policies, ANY = ANY
      ) or (REPORTS_KEY and all(
        r.user.id == g.user.id for r in Docs.by_ids(*kwargs.get(REPORTS_KEY, []))
      ))):
        return abort(make_response('', 403))
      return fn_route(*args, **kwargs)
    return wrapper
  return with_authguard_reports_manage

# viber-channels:manage --has-policies --owns-channels
def authguard_viber_manage(*policies, CHANNELS_KEY = "channelNames", ANY = True):
  def with_authguard_viber_manage(fn_route):
    @wraps(fn_route)
    def wrapper(*args, **kwargs):
      if not (g.user.includes_tags(
        *policies, ANY = ANY
      ) or (CHANNELS_KEY and all(
        ch in g.user.get_profile().get('viber_channels', {}) 
          for ch in kwargs.get(CHANNELS_KEY, [])
      ))):
        return abort(make_response('', 403))
      return fn_route(*args, **kwargs)
    return wrapper
  return with_authguard_viber_manage