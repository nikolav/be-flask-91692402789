
from typing   import List
from typing   import Optional
from enum     import Enum
from uuid     import uuid4 as uuid

from flask import g

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import backref
from sqlalchemy.orm import aliased
from sqlalchemy     import JSON
from sqlalchemy     import union
from sqlalchemy     import or_
from sqlalchemy     import and_

from flask_app import db
from flask_app import io

from . import db
from . import usersTable
from . import assetsTable
from . import ln_assets_tags
from . import ln_users_assets
from . import ln_assets_assets
from . import ln_orders_products
from src.mixins import MixinTimestamps
from src.mixins import MixinIncludesTags
from src.mixins import MixinByIds
from src.mixins import MixinByIdsAndType
from src.mixins import MixinExistsID
from src.mixins import MixinFieldMergeable

from models.docs  import Docs
from models.tags  import Tags

from utils import Unique
from schemas.serialization import SchemaSerializeAssetsTextSearch
from schemas.validation    import SchemaInputPagination
from schemas.validation    import SchemaInputAssetsRows
from schemas.validation    import SchemaInputAssetsRowsArgsOlderThan

from sqlalchemy import event

from flask_app import CATEGORY_KEY_ASSETS_prefix


STRATEGY_order_assets = {
  'date_asc'  : lambda q: q.order_by(Assets.created_at.asc()),
  'date_desc' : lambda q: q.order_by(Assets.created_at.desc()),
}

STRATEGY_assets_rows = {
  'older_than': {
    'schema_args' : SchemaInputAssetsRowsArgsOlderThan,
    'resolve'     : lambda q, args, limit_, *rest: q.where(Assets.created_at < args['older_than']).limit(limit_)
  }
}

class AssetsType(Enum):
  # DIGITAL = "Digital Asset"
  #  communicate announcements; users can not comment in channels
  DIGITAL_CHANNEL = 'DIGITAL_CHANNEL:YqmefT'
  #  custom commnication for users
  DIGITAL_CHAT = 'DIGITAL_CHAT:4nASbEj8pFvqm'
  DIGITAL_FORM = 'DIGITAL_FORM:TzZJs5PZqcWc'
  DIGITAL_POST = 'DIGITAL_POST:6b9959a1-a82c-54a6-b7b2-dbeb285f23d7'
  # all users access
  DIGITAL_CHANNEL_GLOBAL = 'DIGITAL_CHANNEL_GLOBAL:tQ6c5O1mRDtP6fDCCj'
  DIGITAL_CHAT_GLOBAL    = 'DIGITAL_CHAT_GLOBAL:JS4nzSghZq4CZH'
  DIGITAL_FORM_GLOBAL    = 'DIGITAL_FORM_GLOBAL:DKp32J'

  # GROUP = "Group Asset"
  PEOPLE_GROUP_TEAM = 'PEOPLE_GROUP_TEAM:sEdkj9r'

  # PHYSICAL = "Physical Asset"
  PHYSICAL_PRODUCT           = 'PHYSICAL_PRODUCT:u1zDoNxQnYLnHHbp'
  PHYSICAL_STORE             = 'PHYSICAL_STORE:5btoy9I8IKgT0RJO'
  PHYSICAL_DISTRIBUTION_UNIT = 'PHYSICAL_DISTRIBUTION_UNIT:3e854289-02e2-5aa8-85ec-e9d1fc021ea7'

  # DIGITAL_TASKS
  DIGITAL_TASKS = 'DIGITAL_TASKS:5373aab3-2b75-5b19-abcb-419fbf2ffd6f'
  
  # FINANCIAL = "Financial Asset"

  # ISSUES
  ISSUE_GENERAL = 'ISSUE_GENERAL:x53CJbY'

class AssetsDigitalFormFieldTypes(Enum):
  # asset.data
  #   {
  #     fields: [
  #       {
  #         data { question, description, required:bool, multiple:bool },
  #         items: string[],
  #         key,
  #         type
  #       },
  #     ]
  #   }
  
  # @choice: 
  #   .question .description? .required .items: { title:string; value: any; }[] .multiple?
  CHOICE  = 'DIGITAL_FORM:CHOICE:hrNoq9hhbh2wUyZ9fjmf'
  # @text
  #   .question .description? .required
  TEXT    = 'DIGITAL_FORM:TEXT:54QNKF'
  # @boolean
  #   .question .description? .required
  BOOLEAN = 'DIGITAL_FORM:BOOLEAN:P1cUlYS4'
  # @rating
  #   .question .description? .required
  RATING  = 'DIGITAL_FORM:RATING:C6zX66WEWk'
  # @files
  #   .question .description? .required
  FILES   = 'DIGITAL_FORM:FILES:KBr3gZuJAM4s'
  # @table, fill table data
  TABLE_DATA = 'DIGITAL_FORM:TABLE_DATA:GOOGLE_SHEETS:1lbH5rK'
  # @goog.forms, complete google form
  GOOGLE_FORMS = 'DIGITAL_FORM:GOOGLE_FORMS:NWso2XvdHbLlCIW4Q9'


class AssetsStatus(Enum):
  ACTIVE    = 'ACTIVE:YjCrzsLhGtiE4f3ffO'
  ARCHIVED  = 'ARCHIVED:zfbooZxI5IXQmbZIZ'
  CANCELED  = 'CANCELED:2whyBKhy6vv98bPcsUNc'
  CLOSED    = 'CLOSED:bGbGsEnAk2xu9sye7'
  DONE      = 'DONE:6jRIWy6fWT3mT3uNuF2'
  INACTIVE  = 'INACTIVE:fdHJBPHGyC'
  PENDING   = 'PENDING:P4kOFE3HF'

  POSTS_BLOCKED = 'POSTS_BLOCKED:UcAMV'
  POSTS_OPEN    = 'POSTS_OPEN:luIlZa5'


class AssetsCondition(Enum):
  BAD            = 'BAD:oKRchSYlnm8lMqcqoq'
  DEPRECATED     = 'DEPRECATED:stuDFLe7AQf4eKr0RVIn'
  GOOD           = 'GOOD:xW3qMs2e94T9S'
  NEEDS_REPAIR   = 'NEEDS_REPAIR:NJGJD8Spq9A2aFrQgas'
  OUT_OF_SERVICE = 'OUT_OF_SERVICE:KpJUn2IqM2oj'

class AssetsIOEvents(Enum):
  # UPDATE                                      = 'UPDATE:4BPXLhqdWOf:'
  UPDATE                                      = 'IOEVENT:ASSETS:UPDATED:lwzAwwnpz:'
  REMOVE                                      = 'IOEVENT:ASSETS:REMOVED:d3Gcrbv9ezTf7dyb7:'
  IOEVENT_PEOPLE_GROUP_TEAM_CONFIGURED_prefix = 'IOEVENT_PEOPLE_GROUP_TEAM_CONFIGURED:ZNvAgNYKcEG5TNI:'
  IOEVENT_PEOPLE_GROUP_TEAM_REMOVED           = 'IOEVENT_PEOPLE_GROUP_TEAM_REMOVED:7xWnQnU:'
  IOEVENT_SITE_GROUPS_CONFIGRED_prefix        = 'IOEVENT_SITE_GROUPS_CONFIGRED:dx8XECJUjkGwkA:'
  IOEVENT_ASSETS_CONFIGRED_prefix             = 'IOEVENT_ASSETS_CONFIGRED:B11XCb8hAP5:'
  IOEVENT_ASSETS_FORMS_SUBMISSION_prefix      = 'IOEVENT_ASSETS_FORMS_SUBMISSION:kLctvwLigtUAaHzTD:'


class Assets(MixinTimestamps, MixinIncludesTags, MixinByIds, MixinByIdsAndType, MixinExistsID, MixinFieldMergeable, db.Model):
  __tablename__ = assetsTable

  # ID
  id: Mapped[int] = mapped_column(primary_key = True)

  # fields
  name      : Mapped[str] # Descriptive name for the asset (e.g., "Laptop", "Office Space")
  code      : Mapped[Optional[str]] = mapped_column(unique = True) # Identifier.unique for an asset
  type      : Mapped[Optional[str]] # The category of the asset (e.g., "Physical", "Digital", "Financial")
  location  : Mapped[Optional[str]] # Physical or digital location of the asset (e.g., "Warehouse 1", "Cloud Server")
  status    : Mapped[Optional[str]] # Indicates the current status (e.g., "Active", "Disposed", "Maintenance", "Sold")
  condition : Mapped[Optional[str]] # Condition of the asset (e.g., "New", "Good", "Needs Repair")
  notes     : Mapped[Optional[str]] # Detailed description of the asset
  data      : Mapped[Optional[dict]] = mapped_column(JSON) # additional data
  key       : Mapped[Optional[str]]  = mapped_column(default = uuid)

  author_id = mapped_column(db.ForeignKey(f'{usersTable}.id')) # .uid added the asset

  # virtual
  users       : Mapped[List['Users']]  = relationship(secondary = ln_users_assets, back_populates = 'assets') # Who is responsible/belongs for/to asset
  tags        : Mapped[List['Tags']]   = relationship(secondary = ln_assets_tags, back_populates = 'assets') # Additional tags or keywords related to the asset for easier categorization or searchability
  docs        : Mapped[List['Docs']]   = relationship(back_populates = 'asset') # addtional related records
  author      : Mapped['Users']        = relationship(back_populates = 'assets_owned') # Who added the asset
  site_orders : Mapped[List['Orders']] = relationship(back_populates = 'site') # related site
  orders      : Mapped[List['Orders']] = relationship(secondary = ln_orders_products, back_populates = 'products') # related assetSites:orders

  # self-referential, has|belongs-to assets
  assets_has: Mapped[List['Assets']] = relationship(
    secondary      = ln_assets_assets, 
    primaryjoin    = id == ln_assets_assets.c.asset_l_id, 
    secondaryjoin  = id == ln_assets_assets.c.asset_r_id, 
    backref        = backref('assets_belong', lazy='dynamic')
    # back_populates = 'assets'
  )

  
  def tags_add(self, *tags, _commit = True):
    changes = 0

    for tname in filter(lambda p: not self.includes_tags(p), tags):
      tp = Tags.by_name(tname, create = True, _commit = _commit)
      tp.assets.append(self)
      changes += 1
    
    if (0 < changes) and (True == _commit):
      db.session.commit()
    
    return changes

  # public 
  def tags_rm(self, *tags, _commit = True):
    changes = 0

    for tname in filter(lambda p: self.includes_tags(p), tags):
      tp = Tags.by_name(tname, create = True, _commit = _commit)
      tp.assets.remove(self)
      changes += 1
    
    if (0 < changes) and (True == _commit):
      db.session.commit()
    
    return changes
  
  # public
  def is_status(self, s):
    return s == self.status

  # public
  def is_status_active(self):
    return self.is_status(AssetsStatus.ACTIVE.value)
    
  # public
  def serialize_to_text_search(self):
    return ' '.join(v for v in SchemaSerializeAssetsTextSearch().dump(self).values() if v).lower()
  
  # public
  def assets_join(self, *lss):
    changes = 0
    for s in filter(lambda s: s not in self.assets_belong, lss):
      self.assets_belong.append(s)
      changes += 1

    return changes
  
  # public
  def assets_leave(self, *lss):
    changes = 0
    for s in filter(lambda s: s in self.assets_belong, lss):
      self.assets_belong.remove(s)
      changes += 1

    return changes
    
  # public
  def category_key(self):
    return db.session.scalar(
      db.select(
        Tags.tag
      ).join(
        Assets.tags
      ).where(
        self.id == Assets.id,
        Tags.tag.startswith(CATEGORY_KEY_ASSETS_prefix)
      ))

  # public
  def category_key_commit(self, c_key, *, _commit = True):
    _status = False
    if c_key:
      c_tag = f'{CATEGORY_KEY_ASSETS_prefix}{c_key}'
      if c_tag != self.category_key():
        self.category_key_drop(_commit = _commit)
        c = Tags.by_name(c_tag, create = True, _commit = _commit)
        c.assets.append(self)
        if _commit:
          db.session.commit()
        _status = True
    
    return _status

  # public
  def category_key_drop(self, *, _commit = True):
    changes = 0

    for ct in filter(lambda t: t.tag.startswith(CATEGORY_KEY_ASSETS_prefix), self.tags):
      ct.assets.remove(self)
      changes += 1
    
    if 0 < changes:
      if _commit:
        db.session.commit()

    return changes
  
  # public
  def data_updated(self, patch):
    return self.dataField_updated(patch = patch)
  
  # public
  def data_update(self, *, patch, merge = True):
    patched = self.data_updated(patch) if merge else patch
    self.dataField_update(patch = patched)

  # public
  def get_data(self):
    d = self.data if None != self.data else {}
    return d.copy()

  # public
  def ioemit_update(self):
    io.emit(f'{AssetsIOEvents.UPDATE.value}{self.id}')


  # ACTIVE    = 'ACTIVE:YjCrzsLhGtiE4f3ffO'
  # ARCHIVED  = 'ARCHIVED:zfbooZxI5IXQmbZIZ'
  # CANCELED  = 'CANCELED:2whyBKhy6vv98bPcsUNc'
  # CLOSED    = 'CLOSED:bGbGsEnAk2xu9sye7'
  # DONE      = 'DONE:6jRIWy6fWT3mT3uNuF2'
  # INACTIVE  = 'INACTIVE:fdHJBPHGyC'
  # PENDING   = 'PENDING:P4kOFE3HF'

  # POSTS_BLOCKED = 'POSTS_BLOCKED:UcAMV'
  # POSTS_OPEN    = 'POSTS_OPEN:luIlZa5'

  @staticmethod
  def groups_related_assets_authored(*uids, 
                                    ASSETS_TYPES, 
                                    BLACKLIST_ASSET_STATUSES = (), 
                                    WHITELIST_ASSET_TAGS = (), 
                                    EXCLUDE_MY_ASSETS = False,
                                    ORDERED = None,
                                    PAGINATION = None,
                                    # ASSETS_ROWS: {gt:ID, limit:numner}
                                    ASSETS_ROWS = None,
                                  ):
    # what (readable) assets other accounts I share groups with have created

    # PAGINATION: {page:number, per_page:number}
    
    from models.users import Users


    if not uids:
      uids = [g.user.id]
    
    # get related groups IDs
    # ..get my groups
    sq_groups_lookup = db.select(
        Assets.id
      ).join(
        Assets.users
      ).where(
        AssetsType.PEOPLE_GROUP_TEAM.value == Assets.type,
        Users.id.in_(uids)
      )
      # ).subquery()
      
    # get groups related users; users in this groups
    quids = db.select(
        Users.id
      ).distinct().join(
        Users.assets
      ).where(
        Assets.id.in_(sq_groups_lookup)
      )
      # ).subquery()
      
    # select from assets, type, where author in quids
    q_aids = db.select(
      Assets.id
    ).where(
      # ASSET_TYPE == Assets.type,
      Assets.type.in_(ASSETS_TYPES),
      Assets.author_id.in_(quids),
      # ~Assets.status.in_(BLACKLIST_ASSET_STATUSES),
      or_(
        # pass my assets
        g.user.id == Assets.author_id,
        # pass unknown asset:status
        Assets.status.is_(None),
        # skip blacklisted
        and_(
          Assets.status.is_not(None),
          ~Assets.status.in_(BLACKLIST_ASSET_STATUSES),
        )
      )
    )
    
    # pickup tagged assets --any-author
    #  ..for passing shareable posts
    if WHITELIST_ASSET_TAGS:
      q_aids_wl_tags = db.select(
          Assets.id
        ).join(
          Assets.tags
        ).where(
          Assets.type.in_(ASSETS_TYPES),
          or_(
            Assets.status.is_(None),
            # skip if asset is both global and blocked
            and_(
              Assets.status.is_not(None),
              ~Assets.status.in_(BLACKLIST_ASSET_STATUSES),
              Tags.tag.in_(WHITELIST_ASSET_TAGS),
            )
          )
        )
      q_aids = union(q_aids, q_aids_wl_tags)
    

    # skip assets I created if requested
    if True == EXCLUDE_MY_ASSETS:
      q_aids = q_aids.where(
        g.user.id != Assets.author_id)
    
    
    q = db.select(
        Assets
      ).where(
        # Assets.id.in_(q_aids.subquery()))
        Assets.id.in_(q_aids))
    
    # @@
    if PAGINATION:
      pg = None
      
      try:
        pg = SchemaInputPagination().load(PAGINATION)
      
      except Exception as err:
        raise err
        # pass
      
      else:
        limit_  = pg['per_page']
        offset_ = (pg['page'] - 1) * limit_
        q = q.limit(limit_).offset(offset_)
    
    if ASSETS_ROWS:
      rows = None
      
      try:
        rows = SchemaInputAssetsRows().load(ASSETS_ROWS)
        
        strategy_ = rows['strategy']
        args_     = STRATEGY_assets_rows[strategy_]['schema_args']().load(rows['args'])
        limit_    = rows['limit']
        
        q = STRATEGY_assets_rows[strategy_]['resolve'](q, args_, limit_)

      except:
        raise
    
    # order if requested
    if ORDERED and ORDERED in STRATEGY_order_assets:
      q = STRATEGY_order_assets[ORDERED](q)
        
    
    return db.session.scalars(q)
  
  
  @staticmethod
  def assets_parents(*lsa, PtAIDS = None, TYPE = None, DISTINCT = True, WITH_OWN = True):
    '''
      list provided node's parent assets; that contain provided nodes;
      # for account's groups related parent assets:sites
        @PtAIDS; only provided parent assets IDs
        @WITH_OWN; include assets created by this account
    '''
    aids = map(lambda a: a.id, lsa)
    AssetsAliasedParent = aliased(Assets)
    q = db.select(
      AssetsAliasedParent.id
    ).join(
      ln_assets_assets,
      ln_assets_assets.c.asset_l_id == AssetsAliasedParent.id
    ).join(
      Assets,
      ln_assets_assets.c.asset_r_id == Assets.id
    ).where(
      Assets.id.in_(aids))

    if TYPE:
      q = q.where(
        TYPE == AssetsAliasedParent.type)
    
    if PtAIDS:
      q = q.where(
        AssetsAliasedParent.id.in_(PtAIDS))
    
    if DISTINCT:
      q = q.distinct()
    
    if True == WITH_OWN:
      # union created assets:sites
      q_own = db.select(
        Assets.id
      ).where(
        g.user.id == Assets.author_id)
      if TYPE:
        q_own = q_own.where(
          TYPE == Assets.type)

      q = union(q, q_own)
        
    # subq = q.subquery()
    
    return db.session.scalars(
      db.select(
        Assets
      ).where(
        # Assets.id.in_(subq)))
        Assets.id.in_(q)))

  @staticmethod
  def assets_children(*lsa, TYPE = None, DISTINCT = True):
    '''
      list provided node's child assets; that belong to provided nodes
    '''
    aids = map(lambda a: a.id, lsa)
    AssetsAliasedParrent = aliased(Assets)
    q = db.select(
      Assets.id
    ).join(
      ln_assets_assets,
      ln_assets_assets.c.asset_r_id == Assets.id
    ).join(
      AssetsAliasedParrent,
      ln_assets_assets.c.asset_l_id == AssetsAliasedParrent.id
    ).where(
      AssetsAliasedParrent.id.in_(aids))
    
    if None != TYPE:
      q = q.where(
        TYPE == Assets.type)
    
    if DISTINCT:
      q = q.distinct()
    
    # subq = q.subquery()
    
    return db.session.scalars(
      db.select(
        Assets
      ).where(
        # Assets.id.in_(subq)))
        Assets.id.in_(q)))

  @staticmethod
  def codegen(*, length = 4, prefix = 'Assets:'):
    return f'{prefix}{Unique.id(length = length)}'

  @staticmethod
  def products_all():
    return db.session.scalars(
      db.select(
        Assets
      ).where(
        AssetsType.PHYSICAL_PRODUCT.value == Assets.type
      ))
  
  @staticmethod
  def groups_all():
    return db.session.scalars(
      db.select(
        Assets
      ).where(
        AssetsType.PEOPLE_GROUP_TEAM.value == Assets.type
      ))

  @staticmethod
  def groups_only(gids):
    '''
      list groups by provided ids
    '''
    return db.session.scalars(
      db.select(
        Assets
      ).where(
        AssetsType.PEOPLE_GROUP_TEAM.value == Assets.type,
        Assets.id.in_(gids)
      ))

  @staticmethod
  def stores_all():
    return db.session.scalars(
      db.select(
        Assets
      ).where(
        AssetsType.PHYSICAL_STORE.value == Assets.type
      ))

  @staticmethod
  def nuxt_products_prerender():
    q = db.select(
      Assets.id
    ).where(
      AssetsType.PHYSICAL_PRODUCT.value == Assets.type,
      or_(
        Assets.status.is_(None),
        and_(
          Assets.status.isnot(None),
          AssetsStatus.ARCHIVED.value != Assets.status,
        )
      )
    )
    
    return db.session.scalars(q)


# bind listener for Assets:group .location 
#  update lat:lng @data.coords if location provided
@event.listens_for(Assets.location, 'set')
def on_updated_assets_sites_location(asset, value, _oldvalue, _initiator):
  changes = 0
  if (AssetsType.PEOPLE_GROUP_TEAM.value == asset.type):
    if not value:
      # @empty, clear current lat:lng
      asset.data_update(
        patch = {
          'coords': None
        })
      changes += 1

    else:
      from servcies.googlemaps import geocode_address
      res = geocode_address(value)
      asset.data_update(
        patch = {
          'coords': None if res['error'] else res['status']['coords']})
      changes += 1
    
    if 0 < changes:
      db.session.commit()
  

##
## assets table fields @chatGPT response
##

# When designing a database table for managing general company assets, you'll want to include fields that capture essential details about each asset. Here’s a basic outline of fields you might include:

# AssetID (Primary Key): A unique identifier for each asset.
# AssetName: The name or description of the asset.
# Category: The category or type of asset (e.g., IT equipment, furniture, vehicles).
# Location: The physical location or department where the asset is stored.
# PurchaseDate: The date the asset was acquired.
# PurchasePrice: The cost of acquiring the asset.
# CurrentValue: The current value of the asset (may be updated periodically).
# Condition: The current condition of the asset (e.g., New, Good, Needs Repair).
# SerialNumber: A unique serial number or identification number assigned to the asset.
# WarrantyExpiration: The expiration date of the asset’s warranty, if applicable.
# LastServiceDate: The date of the last maintenance or service performed on the asset.
# AssignedTo: The person or department to which the asset is assigned.
# Status: The current status of the asset (e.g., In Use, In Storage, Disposed).
# Notes: Any additional notes or comments about the asset.

# google_calendar :config
#  .data.shareable_link
#  .data.public_url

