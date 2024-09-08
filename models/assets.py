from typing import List
from typing import Optional
from enum   import Enum

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy     import JSON

from . import db
from . import assetsTable
from . import ln_assets_tags
from . import ln_users_assets
from src.mixins import MixinTimestamps
from src.mixins import MixinIncludesTags


class AssetsType(Enum):
  PHYSICAL_SHOP = '5btoy9I8IKgT0RJO'
  # PHYSICAL = "Physical Asset"
  # DIGITAL = "Digital Asset"
  # FINANCIAL = "Financial Asset"

class AssetsStatus(Enum):
  ACTIVE  = 'YjCrzsLhGtiE4f3ffO'
  PENDING = 'P4kOFE3HF'
  CLOSED  = 'bGbGsEnAk2xu9sye7'

class AssetsCondition(Enum):
  GOOD         = 'xW3qMs2e94T9S'
  BAD          = 'oKRchSYlnm8lMqcqoq'
  NEEDS_REPAIR = 'NJGJD8Spq9A2aFrQgas'

class Assets(MixinTimestamps, MixinIncludesTags, db.Model):
  __tablename__ = assetsTable

  # ID
  id: Mapped[int] = mapped_column(primary_key = True)

  # fields
  name      : Mapped[str] # Descriptive name for the asset (e.g., "Laptop", "Office Space")
  code      : Mapped[Optional[str]] # Identifier for an asset
  type      : Mapped[Optional[str]] # The category of the asset (e.g., "Physical", "Digital", "Financial")
  location  : Mapped[Optional[str]] # Physical or digital location of the asset (e.g., "Warehouse 1", "Cloud Server")
  status    : Mapped[Optional[str]] # Indicates the current status (e.g., "Active", "Disposed", "Maintenance", "Sold")
  condition : Mapped[Optional[str]] # Condition of the asset (e.g., "New", "Good", "Needs Repair")
  meta      : Mapped[Optional[dict]] = mapped_column(JSON) # additional data
  notes     : Mapped[Optional[str]] # Detailed description of the asset

  # virtual
  users : Mapped[List['Users']] = relationship(secondary = ln_users_assets, back_populates = 'assets') # Who is responsible for the asset
  tags  : Mapped[List['Tags']]  = relationship(secondary = ln_assets_tags, back_populates = 'assets') # Additional tags or keywords related to the asset for easier categorization or searchability
  docs  : Mapped[List['Docs']]  = relationship(back_populates = 'asset') # addtional related records

