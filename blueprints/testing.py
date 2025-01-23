
from flask       import Blueprint
from flask_cors  import CORS

from src.classes import ResponseStatus


bp_testing = Blueprint('testing', __name__, url_prefix = '/test')

# cors blueprints as wel for cross-domain requests
CORS(bp_testing)

@bp_testing.route('/', methods = ('POST',))
def testing_home():
  from flask_app import mongo
  from schemas.serialization import schemaSerializeMongoDocument
  from flask_app import io
  # from marshmallow import INCLUDE
  # from utils.id_gen import id_gen


  r = ResponseStatus()

  io.emit('status:foo', {'x': 1})
  # mongo.db.foobars.insert_one({'foo': id_gen(), 'bar': id_gen()})

  r.status = 'ok'
  
  return r.dump()

