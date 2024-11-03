
from flask_redis import FlaskRedis


print('@redis:init')

client = None
error  = None

def redis_init(app):
  global client
  global error

  if client:
    return (None, client)
  
  try:
    client = FlaskRedis()
    client.init_app(app)
  
  except Exception as err:
    error = err
  
  return (error, client)

