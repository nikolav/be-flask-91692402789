from flask       import Blueprint
from flask_cors  import CORS

bp_testing = Blueprint('testing', __name__, url_prefix = '/test')

# cors blueprints as wel for cross-domain requests
CORS(bp_testing)


@bp_testing.route('/', methods = ('POST',))
def testing_home():  
  from flask_app import db
  from models.users import Users
  from schemas.serialization import SchemaSerializeUsersTimes
  u = db.session.get(Users, 1)

  return SchemaSerializeUsersTimes(exclude = ('password', 'posts', 'products',)).dump(u)

  return []

