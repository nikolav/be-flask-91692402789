from typing import List

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from . import tagsTable
from . import db
from . import ln_docs_tags
from . import ln_users_tags
from . import ln_products_tags
from . import ln_orders_tags
from . import ln_posts_tags



# https://docs.sqlalchemy.org/en/20/tutorial/metadata.html#declaring-mapped-classes
class Tags(db.Model):
  __tablename__ = tagsTable

  id: Mapped[int] = mapped_column(primary_key = True)

  tag: Mapped[str] = mapped_column(unique = True)

  # virtual
  users   : Mapped[List['Users']]    = relationship(secondary = ln_users_tags,    back_populates = 'tags')
  products: Mapped[List['Products']] = relationship(secondary = ln_products_tags, back_populates = 'tags')
  orders  : Mapped[List['Orders']]   = relationship(secondary = ln_orders_tags,   back_populates = 'tags')
  docs    : Mapped[List['Docs']]     = relationship(secondary = ln_docs_tags,     back_populates = 'tags')
  posts   : Mapped[List['Posts']]    = relationship(secondary = ln_posts_tags,    back_populates = 'tags')

  # magic
  def __repr__(self):
    return f'Tags(id={self.id!r}, tag={self.tag!r})'
  
  def __str__(self):
    # return super().__str__()
    return self.tag


  @staticmethod
  def by_name(tag_name, *, create = False):
    tag = None

    try:
      tag = db.session.scalar(
        db.select(Tags).where(Tags.tag == tag_name)
      )

    except Exception as error:
      raise error

    else:
      if not tag:
        if True == create:
          tag = Tags(tag = tag_name)
          db.session.add(tag)
          db.session.commit()
    
    return tag
