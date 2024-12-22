
from flask       import Blueprint
from flask_cors  import CORS

from src.classes import ResponseStatus


bp_testing = Blueprint('testing', __name__, url_prefix = '/test')

# cors blueprints as wel for cross-domain requests
CORS(bp_testing)

@bp_testing.route('/', methods = ('POST',))
def testing_home():
  from flask_app import db
  from models.users import Users
  from models.assets import Assets
  from models.orders import Orders


  r = ResponseStatus()  
  u = db.session.get(Users, 1)
  a = db.session.get(Assets, 7)

  o = Orders(
    author = u,
    site   = a,
  )
  db.session.add(o)
  db.session.commit()
  
  return r.dump()

