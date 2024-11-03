
from flask_session import Session


initialized = False
sess        = None
error       = None

def session_redis_init(app, *, redis = None):
  global sess
  global error
  global initialized

  if not initialized:  
    if redis:
      try:
        _err, client = redis
        if not client:
          raise Exception('--redis-init-error')
        
        app.config['SESSION_TYPE']  = 'redis'
        app.config['SESSION_REDIS'] = client._redis_client

        sess = Session()
        sess.init_app(app)
        

      except Exception as err:
        error = err
    
    initialized = True

