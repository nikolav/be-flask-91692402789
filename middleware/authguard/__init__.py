from functools import wraps

from flask import g
from flask import abort
from flask import make_response

from models.assets import Assets


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
      if not g.user.includes_tags(
        *policies, ANY = ANY
      ) or not (ASSETS_OWN and all(
        a.author.id == g.user.id for a in Assets.by_ids(*kwargs.get(ASSETS_OWN, []))
      )):
        return abort(make_response('', 403))
      return fn_route(*args, **kwargs)
    return wrapper
  return with_authguard_assets_own

