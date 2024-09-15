import os
import shutil
from typing import List
from typing import Optional

from sqlalchemy     import func
from sqlalchemy     import JSON
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from . import db
from . import usersTable
from . import ln_users_tags
from . import ln_users_assets
from . import POLICY_APPROVED
from src.mixins import MixinTimestamps
from src.mixins import MixinIncludesTags

from models.tags     import Tags
from models.docs     import Docs
from models.products import Products

from utils.str import match_after_last_at
from utils.pw  import hash as hashPassword

POLICY_ADMINS         = os.getenv('POLICY_ADMINS')
TAG_ARCHIVED          = os.getenv('TAG_ARCHIVED')
TAG_EMAIL_VERIFIED    = os.getenv('TAG_EMAIL_VERIFIED')
UPLOAD_PATH           = os.getenv('UPLOAD_PATH')
USER_EMAIL            = os.getenv('USER_EMAIL')

POLICY_APPROVED    = os.getenv('POLICY_APPROVED')
POLICY_EMAIL       = os.getenv('POLICY_EMAIL')
POLICY_FILESTORAGE = os.getenv('POLICY_FILESTORAGE')


class Users(MixinTimestamps, MixinIncludesTags, db.Model):
  __tablename__ = usersTable
  
  id: Mapped[int] = mapped_column(primary_key = True)
  
  email    : Mapped[str] = mapped_column(unique = True)
  password : Mapped[str]
  profile  : Mapped[Optional[dict]] = mapped_column(JSON)
  
  # virtual
  tags     : Mapped[List['Tags']]     = relationship(secondary = ln_users_tags, back_populates = 'users')
  products : Mapped[List['Products']] = relationship(back_populates = 'user')
  orders   : Mapped[List['Orders']]   = relationship(back_populates = 'user')
  posts    : Mapped[List['Posts']]    = relationship(back_populates = 'user')
  docs     : Mapped[List['Docs']]     = relationship(back_populates = 'user')
  assets   : Mapped[List['Assets']]   = relationship(secondary = ln_users_assets, back_populates = 'users')

  # magic
  def __repr__(self):
    return f'<Users(id={self.id!r}, email={self.email!r})>'
    
  # public
  def email_verified(self):
    return self.includes_tags(TAG_EMAIL_VERIFIED)
  
  # public
  def set_email_verified(self, flag = True):
    pe  = Tags.by_name(TAG_EMAIL_VERIFIED)
    isv = self.email_verified()
    
    if flag:
      if not isv:
        pe.users.append(self)

    else:
      if isv:
        pe.users.remove(self)
      
    db.session.commit()

    return self.email_verified()
  
  # public
  def is_admin(self):
    return self.includes_tags(POLICY_ADMINS)
    
  # public
  def approved(self):
    return self.includes_tags(POLICY_APPROVED)
        
  # public 
  def disapprove(self):
    error = '@error:disapprove'

    try:
      if self.approved():
        tag_approved = Tags.by_name(POLICY_APPROVED)
        tag_approved.users.remove(self)
        db.session.commit()

    except Exception as err:
      error = err
    
    else:
      return str(self.id)
    
    return { 'error': str(error) }
  
  # public
  def approve(self):
    error = '@error:approve'

    try:
      if not self.approved():
        tag_approved = Tags.by_name(POLICY_APPROVED)
        tag_approved.users.append(self)
        db.session.commit()

    except Exception as err:
      error = err

    else:
      return str(self.id)
    
    return { 'error': str(error) }
  
  # public
  def get_profile(self):
    return self.profile if self.profile else {}
  
  # public
  def profile_updated(self, **kwargs_fields):
    p = self.get_profile().copy()
    p.update(kwargs_fields)
    return p
  
  # public
  def profile_update(self, **kwargs_fields):
    self.profile = self.profile_updated(**kwargs_fields)
  
  # public
  # def profile(self):
  #   p = None
    
  #   try:

  #     # get profile tag prefix in .tags
  #     profile_domain = Docs.docs_profile_domain_from_uid(self.id)
      
  #     # fetch Tags{}
  #     t = db.session.scalar(
  #       db.select(Tags)
  #         .where(Tags.tag.startswith(profile_domain))
  #     )
      
  #     if not t:
  #       raise Exception('profile:unavailable')
      
  #     # docid from Tags{}
  #     docid = int(match_after_last_at(t.tag))

  #     doc = db.session.get(Docs, docid)
  #     p   = getattr(doc, 'data')
      
  #   except Exception as err:
  #     print(err)

  #   return p if p else {}
  
  # public
  def is_archived(self):
    return self.includes_tags(TAG_ARCHIVED)
  
  # public
  def set_is_archived(self, flag = True):
    pa   = Tags.by_name(TAG_ARCHIVED)
    isar = self.is_archived()
    
    if flag:
      if not isar:
        pa.users.append(self)
    else:
      if isar:
        pa.users.remove(self)
    
    db.session.commit()

    return self.is_archived()

  # public
  def products_sorted_popular(self):
    return Products.popular_sorted_user(self)
  
  # public 
  def policies_add(self, *policies):
    changes = 0

    for policy in filter(lambda p: not self.includes_tags(p), policies):
      tp = Tags.by_name(policy, create = True)
      tp.users.append(self)
      changes += 1
    
    if 0 < changes:
      db.session.commit()

  # public 
  def policies_rm(self, *policies):
    changes = 0

    for policy in filter(lambda p: self.includes_tags(p), policies):
      tp = Tags.by_name(policy, create = True)
      tp.users.remove(self)
      changes += 1
    
    if 0 < changes:
      db.session.commit()
  
  @staticmethod
  def clear_storage(uid):
    directory = os.path.join(UPLOAD_PATH.rstrip("/\\"), 'storage', str(uid))
    if os.path.exists(directory) and os.path.isdir(directory):
      for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        try:
          if os.path.isfile(file_path) or os.path.islink(file_path):
            os.remove(file_path)
            print(f"Removed file: {file_path}")
          elif os.path.isdir(file_path):
            shutil.rmtree(file_path)
            print(f"Removed directory: {file_path}")
        except Exception as e:
          print(f'Failed to delete {file_path}. Reason: {e}')

  @staticmethod
  def create_user(*, email, password):
    u = Users(
      email    = email,
      password = hashPassword(password)
    )

    db.session.add(u)
    db.session.commit()

    # add default policies
    u.policies_add(
      POLICY_APPROVED,
      POLICY_EMAIL,
      POLICY_FILESTORAGE)

    return u

  @staticmethod
  def is_default(id):
    try:
      return id == db.session.scalar(
        db.select(Users.id)
          .where(Users.email == USER_EMAIL))
    except:
      pass
    
    return False
  
  @staticmethod
  def email_exists(email):
    return 0 < db.session.scalar(
      db.select(func.count(Users.id))
        .where(Users.email == email)
    )

