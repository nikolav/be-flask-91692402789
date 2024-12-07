from flask       import Blueprint
from flask_cors  import CORS

from src.classes import ResponseStatus


bp_testing = Blueprint('testing', __name__, url_prefix = '/test')

# cors blueprints as wel for cross-domain requests
CORS(bp_testing)

@bp_testing.route('/', methods = ('POST',))
def testing_home():  
  from models.assets import Assets
  from  flask_app import db
  a = db.session.get(Assets, 166)
  r = ResponseStatus()
  print('a.created_at')
  print(type(a.created_at))
  print(a.created_at.timestamp())
  return r.dump()

