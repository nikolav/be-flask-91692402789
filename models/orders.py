
from enum import Enum

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

from .tags import Tags


class OrdersIOEvents(Enum):
  IOEVENT_ORDERS_CONFIGRED_prefix = 'IOEVENT_ORDERS_CONFIGRED:b6c6caf1-9be2-57a5-9ba0-6254e59d6909:'

class OrdersTags(Enum):
  TAG_ORDERS_SHAREABLE_GLOBALY = 'TAG_ORDERS_SHAREABLE_GLOBALY:61cde3f6-cdf8-5769-bf11-93b91f4ff49d'


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
  

  # public
  def tags_add(self, *tags, _commit = True):
    changes = 0

    for tname in filter(lambda p: not self.includes_tags(p), tags):
      tp = Tags.by_name(tname, create = True, _commit = _commit)
      tp.orders.append(self)
      changes += 1
    
    if (0 < changes) and (True == _commit):
      db.session.commit()
    
    return changes
  
  
  # public
  def tags_rm(self, *tags, _commit = True):
    changes = 0

    for tname in filter(lambda p: self.includes_tags(p), tags):
      tp = Tags.by_name(tname, create = True, _commit = _commit)
      tp.orders.remove(self)
      changes += 1
    
    if (0 < changes) and (True == _commit):
      db.session.commit()
    
    return changes
