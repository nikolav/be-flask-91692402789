
from typing import List
from typing import Optional

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy import JSON

from . import db
from . import assetsTable
from . import ln_assets_tags
from . import ln_users_assets
from src.mixins import MixinTimestamps
from src.mixins import MixinIncludesTags


class Assets(MixinTimestamps, MixinIncludesTags, db.Model):
  __tablename__ = assetsTable

  id: Mapped[int] = mapped_column(primary_key = True)

  name    : Mapped[str]
  code    : Mapped[Optional[str]]
  status  : Mapped[Optional[str]]
  meta    : Mapped[Optional[dict]] = mapped_column(JSON)
  notes   : Mapped[Optional[str]]

  # virtual
  users : Mapped[List['Users']] = relationship(secondary = ln_users_assets, back_populates = 'assets')
  tags  : Mapped[List['Tags']]  = relationship(secondary = ln_assets_tags, back_populates = 'assets')
  docs  : Mapped[List['Docs']]  = relationship(back_populates = 'asset')

