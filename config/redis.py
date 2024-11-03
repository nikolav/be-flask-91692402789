
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

      # access internal redis{} @redis-py
      #  client._redis_client


    except Exception as err:
      error = err
    
    
    initialized = True
    
  
  return (error, client)

