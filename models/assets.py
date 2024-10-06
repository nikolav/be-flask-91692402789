from typing import List
from typing import Optional
from enum   import Enum

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import backref
from sqlalchemy     import JSON

from flask_app import db

from . import db
from . import usersTable
from . import assetsTable
from . import ln_assets_tags
from . import ln_users_assets
from . import ln_assets_assets
from src.mixins import MixinTimestamps
from src.mixins import MixinIncludesTags

from models.docs import Docs
from models.tags import Tags
from models.docs import DocsTags


class AssetsType(Enum):
  # DIGITAL = "Digital Asset"
  #  communicate announcements; users can not comment in channels
  DIGITAL_CHANNEL   = 'DIGITAL_CHANNEL:YqmefT'
  #  custom commnication for users
  DIGITAL_CHAT      = 'DIGITAL_CHAT:4nASbEj8pFvqm'
  DIGITAL_FORM      = 'DIGITAL_FORM:TzZJs5PZqcWc'

  # GROUP = "Grop Asset"
  PEOPLE_GROUP_TEAM = 'PEOPLE_GROUP_TEAM:sEdkj9r'

  # PHYSICAL = "Physical Asset"
  PHYSICAL_PRODUCT  = 'PHYSICAL_PRODUCT:u1zDoNxQnYLnHHbp'
  PHYSICAL_STORE    = 'PHYSICAL_STORE:5btoy9I8IKgT0RJO'

  # FINANCIAL = "Financial Asset"


class AssetsStatus(Enum):
  ACTIVE   = 'ACTIVE:YjCrzsLhGtiE4f3ffO'
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


class Assets(MixinTimestamps, MixinIncludesTags, db.Model):
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

  author_id = mapped_column(db.ForeignKey(f'{usersTable}.id')) # .uid added the asset

  # virtual
  users  : Mapped[List['Users']]  = relationship(secondary = ln_users_assets, back_populates = 'assets') # Who is responsible/belongs for/to asset
  tags   : Mapped[List['Tags']]   = relationship(secondary = ln_assets_tags, back_populates = 'assets') # Additional tags or keywords related to the asset for easier categorization or searchability
  docs   : Mapped[List['Docs']]   = relationship(back_populates = 'asset') # addtional related records
  author : Mapped['Users']        = relationship(back_populates = 'assets_owned') # Who added the asset

  # self-referential association, has|belongs-to assets
  assets_has: Mapped[List['Assets']] = relationship(
    secondary      = ln_assets_assets, 
    primaryjoin    = id == ln_assets_assets.c.asset_l_id, 
    secondaryjoin  = id == ln_assets_assets.c.asset_r_id, 
    backref        = backref( 'assets_belong', lazy='dynamic')
    # back_populates = 'assets'
  )

  
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
