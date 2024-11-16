
from flask import g

from typing import List
from typing import Optional
from enum   import Enum
from uuid   import uuid4 as uuid

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import backref
from sqlalchemy.orm import aliased
from sqlalchemy     import JSON
from sqlalchemy     import union

from flask_app import db
from flask_app import io

from . import db
from . import usersTable
from . import assetsTable
from . import ln_assets_tags
from . import ln_users_assets
from . import ln_assets_assets
from src.mixins import MixinTimestamps
from src.mixins import MixinIncludesTags
from src.mixins import MixinByIds
from src.mixins import MixinByIdsAndType
from src.mixins import MixinExistsID
from src.mixins import MixinFieldMergeable

from models.docs import Docs
from models.tags import Tags
from models.docs import DocsTags

from utils import Unique
from schemas.serialization import SchemaSerializeAssetsTextSearch


CATEGORY_KEY_ASSETS_prefix = 'CATEGORY_KEY:ASSETS:hhPDiM:'

class AssetsType(Enum):
  # DIGITAL = "Digital Asset"
  #  communicate announcements; users can not comment in channels
  DIGITAL_CHANNEL = 'DIGITAL_CHANNEL:YqmefT'
  #  custom commnication for users
  DIGITAL_CHAT = 'DIGITAL_CHAT:4nASbEj8pFvqm'
  DIGITAL_FORM = 'DIGITAL_FORM:TzZJs5PZqcWc'
  # all users access
  DIGITAL_CHANNEL_GLOBAL = 'DIGITAL_CHANNEL_GLOBAL:tQ6c5O1mRDtP6fDCCj'
  DIGITAL_CHAT_GLOBAL    = 'DIGITAL_CHAT_GLOBAL:JS4nzSghZq4CZH'
  DIGITAL_FORM_GLOBAL    = 'DIGITAL_FORM_GLOBAL:DKp32J'

  # GROUP = "Group Asset"
  PEOPLE_GROUP_TEAM = 'PEOPLE_GROUP_TEAM:sEdkj9r'

  # PHYSICAL = "Physical Asset"
  PHYSICAL_PRODUCT  = 'PHYSICAL_PRODUCT:u1zDoNxQnYLnHHbp'
  PHYSICAL_STORE    = 'PHYSICAL_STORE:5btoy9I8IKgT0RJO'

  # FINANCIAL = "Financial Asset"

  # ISSUES
  ISSUE_GENERAL = 'ISSUE_GENERAL:x53CJbY'


class AssetsStatus(Enum):
  ACTIVE   = 'ACTIVE:YjCrzsLhGtiE4f3ffO'
  ARCHIVED = 'ARCHIVED:zfbooZxI5IXQmbZIZ'
  CANCELED = 'CANCELED:2whyBKhy6vv98bPcsUNc'
  CLOSED   = 'CLOSED:bGbGsEnAk2xu9sye7'
  DONE     = 'DONE:6jRIWy6fWT3mT3uNuF2'
  INACTIVE = 'INACTIVE:fdHJBPHGyC'
  PENDING  = 'PENDING:P4kOFE3HF'


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
  users  : Mapped[List['Users']]  = relationship(secondary = ln_users_assets, back_populates = 'assets') # Who is responsible/belongs for/to asset
  tags   : Mapped[List['Tags']]   = relationship(secondary = ln_assets_tags, back_populates = 'assets') # Additional tags or keywords related to the asset for easier categorization or searchability
  docs   : Mapped[List['Docs']]   = relationship(back_populates = 'asset') # addtional related records
  author : Mapped['Users']        = relationship(back_populates = 'assets_owned') # Who added the asset

  # self-referential, has|belongs-to assets
  assets_has: Mapped[List['Assets']] = relationship(
    secondary      = ln_assets_assets, 
    primaryjoin    = id == ln_assets_assets.c.asset_l_id, 
    secondaryjoin  = id == ln_assets_assets.c.asset_r_id, 
    backref        = backref( 'assets_belong', lazy='dynamic')
    # back_populates = 'assets'
  )

  
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
        ln_assets_tags
      ).join(
        Assets
      ).where(
        self.id == Assets.id,
        Tags.tag.startswith(CATEGORY_KEY_ASSETS_prefix)
      )
    )

  
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

  # public
  def product_images_all(self):
    if self.type == AssetsType.PHYSICAL_PRODUCT.value:
      return db.session.scalars(
        db.select(
          Docs
        ).join(
          Docs.tags
        ).where(
          self.id == Docs.asset_id,
          DocsTags.IMAGE_PRODUCT.value == Tags.tag
        ))
    
    # default
    return []

  
  # public
  def form_submissions_all(self):
    if AssetsType.DIGITAL_FORM.value == self.type:
      return db.session.scalars(
        db.select(
          Docs
        ).join(
          Docs.tags
        ).where(
          self.id == Docs.asset_id,
          Docs.tags.any(
            DocsTags.ASSETS_FORM_SUBMISSION.value == Tags.tag
          )
        ).order_by(
          Docs.created_at.desc()
        ))
    
    # default
    return []


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
        
    subq = q.subquery()
    
    return db.session.scalars(
      db.select(
        Assets
      ).where(
        Assets.id.in_(subq)))

  
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
    
    subq = q.subquery()
    
    return db.session.scalars(
      db.select(
        Assets
      ).where(
        Assets.id.in_(subq)))


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
