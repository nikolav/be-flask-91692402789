
import json

from config.graphql.init    import mutation
from utils.merge_strategies import dict_deepmerger_extend_lists as merger
from src.classes            import ResponseStatus

from flask_app import io
from flask_app import IOEVENT_REDIS_CACHE_KEY_UPDATED_prefix


# cacheRedisCommit(cache_key: String!, patch: JsonData, merge: Boolean): JsonData!
@mutation.field('cacheRedisCommit')
def resolve_cacheRedisCommit(_obj, _info, cache_key, patch = None, merge = True):
  r       = ResponseStatus()
  cache   = None
  changes = 0

  try:
    from flask_app import redis_client
    _err, client = redis_client

    cache = {} if not client.exists(cache_key) else json.loads(client.get(cache_key).decode())
    
    if patch:
      if merge:
        merger.merge(cache, patch)
      else:
        cache = patch

      client.set(cache_key, json.dumps(cache))

      changes += 1


  except Exception as err:
    # raise err
    r.error = err


  else:
    r.status = 'ok'
    if 0 < changes:
      io.emit(f'{IOEVENT_REDIS_CACHE_KEY_UPDATED_prefix}{cache_key}')


  return r.dump()


