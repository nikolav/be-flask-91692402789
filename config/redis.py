
from flask_redis import FlaskRedis


print('@redis:init')

initialized = False

client = None
error  = None

def redis_init(app):
  global client
  global error
  global initialized

  if not initialized:  

    try:
      client = FlaskRedis()
      client.init_app(app)
    
    except Exception as err:
      error = err
    
    initialized = True
    
  
  return (error, client)

