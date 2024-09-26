import os
import re
import json

from enum   import Enum
from typing import List
from typing import Optional

from sqlalchemy     import JSON
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from . import db
from . import docsTable
from . import usersTable
from . import postsTable
from . import productsTable
from . import ordersTable
from . import assetsTable
from . import ln_docs_tags
from .tags import Tags
from src.mixins import MixinTimestamps
from src.mixins import MixinIncludesTags
from src.mixins import MixinExistsID
from schemas.serialization import SchemaSerializeDocJsonTimes
from config import TAG_VARS

from flask_app import VIBER_CHANNELS_DOCID


TAG_USER_PROFILE_prefix = os.getenv('TAG_USER_PROFILE_prefix')

_schemaDocsDump     = SchemaSerializeDocJsonTimes()
_schemaDocsDumpMany = SchemaSerializeDocJsonTimes(many = True)


class DocsTags(Enum):
  ASSETS_FORM_SUBMISSION = 'ASSETS_FORM_SUBMISSION:5JTfkV8'
  

# https://docs.sqlalchemy.org/en/20/tutorial/metadata.html#declaring-mapped-classes
class Docs(MixinTimestamps, MixinIncludesTags, MixinExistsID, db.Model):
  __tablename__ = docsTable

  id   : Mapped[int]  = mapped_column(primary_key = True)
  data : Mapped[dict] = mapped_column(JSON)
  # unique key
  #  get records by unique name
  key  : Mapped[Optional[str]] = mapped_column(unique = True)
  user_id    = mapped_column(db.ForeignKey(f'{usersTable}.id'))
  post_id    = mapped_column(db.ForeignKey(f'{postsTable}.id'))
  product_id = mapped_column(db.ForeignKey(f'{productsTable}.id'))
  order_id   = mapped_column(db.ForeignKey(f'{ordersTable}.id'))
  asset_id   = mapped_column(db.ForeignKey(f'{assetsTable}.id'))
  parent_id  = mapped_column(db.ForeignKey(f'{docsTable}.id'))

  # virtual
  tags     : Mapped[List['Tags']] = relationship(secondary = ln_docs_tags, back_populates = 'docs')
  user     : Mapped['Users']      = relationship(back_populates = 'docs')
  post     : Mapped['Posts']      = relationship(back_populates = 'docs')
  product  : Mapped['Products']   = relationship(back_populates = 'docs')
  order    : Mapped['Orders']     = relationship(back_populates = 'docs')
  asset    : Mapped['Assets']     = relationship(back_populates = 'docs')
  # virtual: hierarchical data
  parent   : Mapped['Docs']       = relationship(back_populates = 'children', remote_side = [id])
  children : Mapped[List['Docs']] = relationship(back_populates = 'parent')
  
  # magic
  def __repr__(self):
    return f'Docs({json.dumps(self.dump())})'
  
  
  @staticmethod
  def viber_channels():
    return Docs.by_key(VIBER_CHANNELS_DOCID, create = True)
  

  @staticmethod
  def tagged(tag_name):
    tag = Tags.by_name(tag_name)
    return tag.docs if tag else []
  
  
  @staticmethod
  def dicts(docs, **kwargs):
    return _schemaDocsDumpMany.dump(docs, **kwargs)
  
    
  @staticmethod
  def by_tag_and_id(tag, id):
    return db.session.scalar(
      db.select(Docs)
        .join(Docs.tags)
        .where(
          Tags.tag == tag, 
          Docs.id  == id))
      
  
  @staticmethod
  def by_key(key, *, create = False):
    d = None
    if key:
      d = db.session.scalar(
        db.select(
          Docs
        ).where(
          key == Docs.key
        )
      )
      if not d:
        if create == True:
          # add
          d = Docs(data = {}, key = key)
          db.session.add(d)
          db.session.commit()
    
    return d
  

  # alias .by_key
  @staticmethod
  def by_doc_id(key, *, create = False):
    return Docs.by_key(key, create = create)
    
  
  # vars
  @staticmethod
  def var_by_name(var_name):
    return db.session.scalar(
      db.select(Docs).join(Docs.tags).where(
        Tags.tag == '@vars', 
        Docs.data.contains(var_name)
      )
    )
  
  
  @staticmethod
  def vars_list():
    res = []
    for doc in Docs.tagged(TAG_VARS):
      for name, value in doc.data.items():
        res.append({ 'id': doc.id, 'name': name, 'value': value })
    return res


  def dump(self, **kwargs):
    return _schemaDocsDump.dump(self, **kwargs)

