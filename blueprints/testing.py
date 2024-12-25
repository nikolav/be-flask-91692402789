
from flask       import Blueprint
from flask_cors  import CORS

from src.classes import ResponseStatus


bp_testing = Blueprint('testing', __name__, url_prefix = '/test')

# cors blueprints as wel for cross-domain requests
CORS(bp_testing)

@bp_testing.route('/', methods = ('POST',))
def testing_home():
  from flask_app import db
  from models.docs import Docs


  r = ResponseStatus()  
  d = db.session.get(Docs, 17)
    
  r.status = d.serialize_to_qsearch()
  
  return r.dump()

