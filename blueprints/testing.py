from flask       import Blueprint
from flask_cors  import CORS

from src.classes import ResponseStatus


bp_testing = Blueprint('testing', __name__, url_prefix = '/test')

# cors blueprints as wel for cross-domain requests
CORS(bp_testing)

@bp_testing.route('/', methods = ('POST',))
def testing_home():  
  from models.assets import Assets
  from flask         import g
  from models.assets import AssetsType
  from schemas.serialization import SchemaSerializeAssets
  r = ResponseStatus()

  lsa = Assets.groups_related_assets_authored( 
          ASSETS_TYPES = (AssetsType.DIGITAL_POST.value,),
          BLACKLIST_ASSET_STATUSES = ('POSTS_BLOCKED:UcAMV',),
          # EXCLUDE_MY_ASSETS = True,
          ORDERED='date_desc',
          # WHITELIST_ASSET_TAGS = ('TAG_ASSETS_SHAREABLE:de0fe927-a79e-505a-8d0c-9cbff5e3ef10',),
          
        )
  
  
  return SchemaSerializeAssets(many=True, only=('id',)).dump(lsa)



