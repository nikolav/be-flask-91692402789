import os

from sqlalchemy import Float
from sqlalchemy import Integer
from sqlalchemy import DateTime

from flask_app import db


from flask_app import PRODUCTION
from flask_app import POLICY_APPROVED

tblSuffix_dev        = os.getenv('TABLE_NAME_SUFFIX_dev')
tblSuffix_production = os.getenv('TABLE_NAME_SUFFIX_production')

tblSuffix = tblSuffix_production if PRODUCTION else tblSuffix_dev


tagsTable     = f'tags{tblSuffix}'
usersTable    = f'users{tblSuffix}'
productsTable = f'products{tblSuffix}'
ordersTable   = f'orders{tblSuffix}'
docsTable     = f'docs{tblSuffix}'
postsTable    = f'posts{tblSuffix}'
assetsTable   = f'assets{tblSuffix}'

lnTableUsersTags      = f'ln_users_tags{tblSuffix}'
lnTableProductsTags   = f'ln_products_tags{tblSuffix}'
lnTableOrdersProducts = f'ln_orders_products{tblSuffix}'
lnTableOrdersTags     = f'ln_orders_tags{tblSuffix}'
lnTableDocsTags       = f'ln_docs_tags{tblSuffix}'
lnTablePostsTags      = f'ln_posts_tags{tblSuffix}'
lnTableAssetsTags     = f'ln_assets_tags{tblSuffix}'
lnTableUsersAssets    = f'ln_users_assets{tblSuffix}'
lnTableAssetsAssets   = f'ln_assets_assets{tblSuffix}'
lnTableUsersUsersFollow = f'ln_users_users_follow{tblSuffix}'
lnTableUsersUsersManage = f'ln_users_users_manage{tblSuffix}'


# link tables, *:*
ln_users_tags = db.Table(
  lnTableUsersTags,
  db.Column('user_id', db.ForeignKey(f'{usersTable}.id'), primary_key = True),
  db.Column('tag_id',  db.ForeignKey(f'{tagsTable}.id'),  primary_key = True),
)

ln_products_tags = db.Table(
  lnTableProductsTags,
  db.Column('product_id', db.ForeignKey(f'{productsTable}.id'), primary_key = True),
  db.Column('tag_id',     db.ForeignKey(f'{tagsTable}.id'),     primary_key = True),
)

ln_orders_products = db.Table(
  lnTableOrdersProducts,
  db.Column('order_id',   db.ForeignKey(f'{ordersTable}.id'),   primary_key = True),
  db.Column('product_id', db.ForeignKey(f'{productsTable}.id'), primary_key = True),
  db.Column('amount', Float),
  db.Column('status', Integer),
  db.Column('delivery_at', DateTime),
)

ln_orders_tags = db.Table(
  lnTableOrdersTags,
  db.Column('order_id', db.ForeignKey(f'{ordersTable}.id'), primary_key = True),
  db.Column('tag_id',   db.ForeignKey(f'{tagsTable}.id'),   primary_key = True),
)

ln_docs_tags = db.Table(
  lnTableDocsTags,
  db.Column('doc_id', db.ForeignKey(f'{docsTable}.id'), primary_key = True),
  db.Column('tag_id', db.ForeignKey(f'{tagsTable}.id'), primary_key = True),
)

ln_posts_tags = db.Table(
  lnTablePostsTags,
  db.Column('post_id', db.ForeignKey(f'{postsTable}.id'), primary_key = True),
  db.Column('tag_id',  db.ForeignKey(f'{tagsTable}.id'),  primary_key = True),
)

ln_assets_tags = db.Table(
  lnTableAssetsTags,
  db.Column('asset_id', db.ForeignKey(f'{assetsTable}.id'), primary_key = True),
  db.Column('tag_id',   db.ForeignKey(f'{tagsTable}.id'),   primary_key = True),
)

ln_users_assets = db.Table(
  lnTableUsersAssets,
  db.Column('user_id',  db.ForeignKey(f'{usersTable}.id'),  primary_key = True),
  db.Column('asset_id', db.ForeignKey(f'{assetsTable}.id'), primary_key = True),
)

ln_assets_assets = db.Table(
  lnTableAssetsAssets,
  db.Column('asset_l_id', db.ForeignKey(f'{assetsTable}.id'),  primary_key = True),
  db.Column('asset_r_id', db.ForeignKey(f'{assetsTable}.id'),  primary_key = True),
)

ln_users_users_follow = db.Table(
  lnTableUsersUsersFollow,
  db.Column('users_l_id', db.ForeignKey(f'{usersTable}.id'),  primary_key = True),
  db.Column('users_r_id', db.ForeignKey(f'{usersTable}.id'),  primary_key = True),
)

ln_users_users_manage = db.Table(
  lnTableUsersUsersManage,
  db.Column('users_l_id', db.ForeignKey(f'{usersTable}.id'),  primary_key = True),
  db.Column('users_r_id', db.ForeignKey(f'{usersTable}.id'),  primary_key = True),
)

