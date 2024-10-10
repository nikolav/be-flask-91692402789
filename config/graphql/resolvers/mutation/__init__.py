from .storage import storage_rm

from .docs import docs_upsert
from .docs import docs_rm
from .docs import doc_upsert
from .docs import docs_tags_manage
from .docs import docs_rm_by_id

from .products import products_rm
from .products import products_upsert

from .orders import orders_place
from .orders import manage_data
from .orders import order_products_status
from .orders import order_products_delivery_date
from .orders import orders_set_completed

from .posts import posts_upsert
from .posts import posts_rm
from .posts import posts_images_drop

from .accounts import account_drop
from .accounts import accounts_add
from .accounts import policies_manage
from .accounts import profile_patch
from .accounts import accounts_send_verify_email_link
from .accounts import verify_email

from .mail import sendmail

from .messaging import cloud_messaging_ping
from .messaging import viber_send_message

from .assets import groups_configure
from .assets import groups_add
from .assets import assets_rm
from .assets import assets_update


