
import json

from enum   import Enum
from typing import List
from typing import Optional

from sqlalchemy     import JSON
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from uuid import uuid4 as uuid

from . import db
from . import docsTable
from . import usersTable
from . import assetsTable
from . import ln_docs_tags

from models.tags import Tags

from src.mixins import MixinTimestamps
from src.mixins import MixinIncludesTags
from src.mixins import MixinExistsID
from src.mixins import MixinFieldMergeable
from src.mixins import MixinByIds

from schemas.serialization import SchemaSerializeDocJsonTimes
from schemas.serialization import SchemaSerializeDocsQStringSearch

from flask_app import VIBER_CHANNELS_DOCID
from flask_app import TAG_STORAGE
from flask_app import TAG_VARS
from flask_app import TAG_IS_FILE

from src.classes.q_search_tokenizer import QSearchTokenizer

# from sqlalchemy import event


_schemaDocsDump     = SchemaSerializeDocJsonTimes()
_schemaDocsDumpMany = SchemaSerializeDocJsonTimes(many = True)


class DocsTags(Enum):
  ASSETS_FORM_SUBMISSION   = 'ASSETS_FORM_SUBMISSION:5JTfkV8'
  IMAGE_PRODUCT            = 'IMAGE_PRODUCT:06koI97IiCW'
  USER_AVAILABILITY_STATUS = 'USER_AVAILABILITY_STATUS:TOy5MSh9d7xmo94vvMED'
  SHAREABLE                = 'DocsTags:SHAREABLE:muSvm4x5'
  TAGGED_CONTACTS          = 'CONTACTS:6249cd68-f04f-5960-a454-7d5a66ecfbaa'
  

# https://docs.sqlalchemy.org/en/20/tutorial/metadata.html#declaring-mapped-classes
class Docs(MixinTimestamps, MixinIncludesTags, MixinExistsID, MixinFieldMergeable, MixinByIds, db.Model):
  __tablename__ = docsTable

  id   : Mapped[int]           = mapped_column(primary_key = True)
  key  : Mapped[Optional[str]] = mapped_column(default = uuid)
  data : Mapped[dict]          = mapped_column(JSON)
  # foreignkey
  user_id    = mapped_column(db.ForeignKey(f'{usersTable}.id'))
  asset_id   = mapped_column(db.ForeignKey(f'{assetsTable}.id'))
  parent_id  = mapped_column(db.ForeignKey(f'{docsTable}.id'))

  # virtual
  tags     : Mapped[List['Tags']] = relationship(secondary = ln_docs_tags, back_populates = 'docs')
  user     : Mapped['Users']      = relationship(back_populates = 'docs')
  asset    : Mapped['Assets']     = relationship(back_populates = 'docs')
  # virtual: hierarchical data
  parent   : Mapped['Docs']       = relationship(back_populates = 'children', remote_side = [id])
  children : Mapped[List['Docs']] = relationship(back_populates = 'parent')
  
  # magic
  def __repr__(self):
    return f'Docs({json.dumps(self.dump())})'
  
    
  # public
  def serialize_to_qsearch(self):
    return ' '.join(QSearchTokenizer().tokenize(' '.join(v for v in SchemaSerializeDocsQStringSearch().dump(self).values() if v)))

    
  # public
  def get_data(self, updates = None):
    d = self.data.copy()
    if None != updates:
      d.update(updates)
    return d
  
  
  @staticmethod
  def users_availabilities():
    return Docs.by_key(DocsTags.USER_AVAILABILITY_STATUS.value, create = True)
  
  
  @staticmethod
  def storage_ls(uid = None):
    return Docs.tagged(TAG_IS_FILE if None == uid else f'{TAG_STORAGE}{uid}')
  
  @staticmethod
  def viber_channels():
    return Docs.by_key(VIBER_CHANNELS_DOCID, create = True)


  @staticmethod
  def tagged(tag_name):
    return db.session.scalars(
      db.select(
        Docs
      ).join(
        Docs.tags
      ).where(
        tag_name == Tags.tag
      ))
  
  
  @staticmethod
  def dicts(docs, **kwargs):
    return _schemaDocsDumpMany.dump(docs, **kwargs)
  
    
  @staticmethod
  def by_tag_and_id(tag, id):
    return db.session.scalar(
      db.select(
        Docs
      ).join(
        Docs.tags
      ).where(
          tag == Tags.tag,
          id  == Docs.id
      ))
      
  
  @staticmethod
  def by_key(key, *, create = False, _commit =  True):
    d = None
    if key:
      d = db.session.scalar(
        db.select(
          Docs
        ).where(
          key == Docs.key
        ))
      
      if not d:
        if True == create:
          # @create:default
          d = Docs(data = {}, key = key)
          db.session.add(d)
          if _commit:
            db.session.commit()
    
    return d
  

  # alias .by_key
  @staticmethod
  def by_doc_id(key, *, create = False, _commit = True):
    return Docs.by_key(key, create = create, _commit = _commit)
    
  
  # vars
  @staticmethod
  def var_by_name(var_name):
    return db.session.scalar(
      db.select(
        Docs
      ).join(
        Docs.tags
      ).where(
        '@vars' == Tags.tag, 
        Docs.data.contains(var_name),
      ))
  
  
  @staticmethod
  def vars_list():
    res = []
    for doc in Docs.tagged(TAG_VARS):
      for name, value in doc.data.items():
        res.append({ 'id': doc.id, 'name': name, 'value': value })
    return res


  def dump(self, **kwargs):
    return _schemaDocsDump.dump(self, **kwargs)

