
from flask_redis import FlaskRedis


print('@redis:init')

def redis_init(app):
  cli   = None
  error = None

  try:
    cli = FlaskRedis()
    cli.init_app(app)
  
  except Exception as err:
    error = err
  
  return (error, cli)
