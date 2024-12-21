
from typing         import Optional
from typing         import List

from uuid           import uuid4 as uuid

from sqlalchemy     import JSON
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from src.mixins import MixinTimestamps
from src.mixins import MixinIncludesTags
from src.mixins import MixinByIds
from src.mixins import MixinExistsID
from src.mixins import MixinFieldMergeable

from . import db
from . import ordersTable
from . import usersTable
from . import assetsTable
from . import ln_orders_tags
from . import ln_orders_products


class Orders(MixinTimestamps, MixinIncludesTags, MixinByIds, MixinExistsID, MixinFieldMergeable, db.Model):
  __tablename__ = ordersTable

  # ID
  id: Mapped[int] = mapped_column(primary_key = True)

  # fields
  key       : Mapped[Optional[str]]  = mapped_column(default = uuid)
  status    : Mapped[Optional[str]]
  data      : Mapped[Optional[dict]] = mapped_column(JSON)
  notes     : Mapped[Optional[str]]
  
  author_id = mapped_column(db.ForeignKey(f'{usersTable}.id'))  # .uid created order
  site_id   = mapped_column(db.ForeignKey(f'{assetsTable}.id')) # .sid related site

  # virtual
  author   : Mapped['Users']        = relationship(back_populates = 'orders') # Who created the order
  site     : Mapped['Assets']       = relationship(back_populates = 'site_orders') # related site
  tags     : Mapped[List['Tags']]   = relationship(secondary = ln_orders_tags,     back_populates = 'orders')
  products : Mapped[List['Assets']] = relationship(secondary = ln_orders_products, back_populates = 'orders')
  