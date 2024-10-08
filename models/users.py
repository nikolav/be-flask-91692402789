import os
import shutil
from typing import List
from typing import Optional
from enum import Enum

from flask import g

from sqlalchemy     import func
from sqlalchemy     import JSON
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from . import db
from . import usersTable
from . import ln_users_tags
from . import ln_users_assets
from src.mixins import MixinTimestamps
from src.mixins import MixinIncludesTags
from src.mixins import MixinByIds

from models.tags     import Tags
from models.docs     import Docs
from models.products import Products
from models.assets   import Assets
from models.assets   import AssetsType

# from utils.str import match_after_last_at
from utils.pw  import hash as hashPassword

from copy import deepcopy
from utils.merge_strategies import dict_deepmerger_extend_lists as merger

from flask_app import KEY_FCM_DEVICE_TOKENS
from flask_app import POLICY_ADMINS
from flask_app import POLICY_APPROVED
from flask_app import POLICY_EMAIL
from flask_app import POLICY_FILESTORAGE
from flask_app import POLICY_MANAGERS
from flask_app import TAG_ARCHIVED
from flask_app import TAG_EMAIL_VERIFIED
from flask_app import TAG_USERS_EXTERNAL
from flask_app import UPLOAD_DIR
from flask_app import UPLOAD_PATH
from flask_app import USER_EMAIL


DEFAULT_USER_CREATE_POLICIES = (
  POLICY_APPROVED, 
  POLICY_EMAIL, 
  POLICY_FILESTORAGE,
)

# https://help.zoho.com/galleryDocuments/edbsne9896a615107dc695c0c42640947c15396f645651fa8eb1ae6632e434ba6231388ce5ff6e47742393c1b76377ff36fff?inline=true
class UsersTagsStatus(Enum):
  AVAILABLE      = 'AVAILABLE:vmWsUhVctBpu1BAp'
  AWAY           = 'AWAY:p2oLyHH'
  BUSY           = 'BUSY:woxs5B8Slw'
  DO_NOT_DISTURB = 'DO_NOT_DISTURB:eb6Y5nXzlK'
  INVISIBLE      = 'INVISIBLE:EDjVu'
  

class Users(MixinTimestamps, MixinIncludesTags, MixinByIds, db.Model):
  __tablename__ = usersTable
  
  id: Mapped[int] = mapped_column(primary_key = True)
  
  email    : Mapped[str] = mapped_column(unique = True)
  password : Mapped[str]
  profile  : Mapped[Optional[dict]] = mapped_column(JSON)
  
  # virtual
  tags         : Mapped[List['Tags']]     = relationship(secondary = ln_users_tags, back_populates = 'users')
  products     : Mapped[List['Products']] = relationship(back_populates = 'user')
  orders       : Mapped[List['Orders']]   = relationship(back_populates = 'user')
  posts        : Mapped[List['Posts']]    = relationship(back_populates = 'user')
  docs         : Mapped[List['Docs']]     = relationship(back_populates = 'user')
  assets       : Mapped[List['Assets']]   = relationship(secondary = ln_users_assets, back_populates = 'users')
  assets_owned : Mapped[List['Assets']]   = relationship(back_populates = 'author') # assets created by the user

  # magic
  def __repr__(self):
    return f'<Users(id={self.id!r}, email={self.email!r})>'
  
  # public
  def assets_belongs_to(self, *lsa, ANY = False):
    return all(
        self in a.users for a in lsa
      ) if not ANY else any(
        self in a.users for a in lsa
      )
    
  # public
  def assets_join(self, *lsa):
    changes = 0
    for g in filter(lambda a: self not in a.users, lsa):
      g.users.append(self)
      changes += 1

    return changes

  # public
  def assets_leave(self, *lsa):
    changes = 0
    for g in filter(lambda a: self in a.users, lsa):
      g.users.remove(self)
      changes += 1

    return changes
  
  # public
  def availability_commit(self, value):
    self.profile_update(patch = { 'availability': value })
    db.session.commit()
  
  # public
  def availability_is(self, value):
    return value == self.get_profile().get('availability')

  # public
  def is_available(self):
    return self.availability_is(UsersTagsStatus.AVAILABLE.value)
  
  # public
  def can_manage_account(self, uid):
    return any((uid == g.user.id, g.user.is_admin(),))
  
  # public
  def cloud_messaging_device_tokens(self):
    '''
      firebase FCM user device tokens
    '''
    try:
      # get tokens Docs{}
      dt  = Docs.by_key(f'{KEY_FCM_DEVICE_TOKENS}{self.id}')
      # generate valid key tokens
      return (k_tok for k_tok, k_val in dt.data.items() if True == k_val)

    except:
      pass

    return []

  # public
  def assets_by_type(self, *types):
    return db.session.scalars(
      db.select(
        Assets
      ).join(
        ln_users_assets
      ).join(
        Users
      ).where(
        Assets.type.in_(types),
        self.id == Users.id
      ))
  
  # public
  def groups(self):
    return self.assets_by_type(AssetsType.PEOPLE_GROUP_TEAM.value)

  # public
  def stores(self):
    return self.assets_by_type(AssetsType.PHYSICAL_STORE.value)
    
  # public
  def is_external(self):
    return self.includes_tags(TAG_USERS_EXTERNAL)
  
  # public
  def set_is_external(self, flag = True):
    if flag:
      self.policies_add(TAG_USERS_EXTERNAL)
    else:
      self.policies_rm(TAG_USERS_EXTERNAL)
    
    return self.is_external()
  
  # public
  def is_manager(self):
    return self.includes_tags(POLICY_MANAGERS)
  
  # public
  def set_is_manager(self, flag = True):
    if flag:
      self.policies_add(POLICY_MANAGERS)
    else:
      self.policies_rm(POLICY_MANAGERS)
    
    return self.is_manager()
  
  # public
  def email_verified(self):
    return self.includes_tags(TAG_EMAIL_VERIFIED)
  
  # public
  def set_email_verified(self, flag = True):
    if flag:
      self.policies_add(TAG_EMAIL_VERIFIED)
    else:
      self.policies_rm(TAG_EMAIL_VERIFIED)

    return self.email_verified()
  
  # public
  def is_admin(self):
    return self.includes_tags(POLICY_ADMINS)
  
  # public
  def set_is_admin(self, flag = True):
    if flag:
      self.policies_add(POLICY_ADMINS)
    else:
      self.policies_rm(POLICY_ADMINS)
    
    return self.is_admin()
    
  # public
  def approved(self):
    return self.includes_tags(POLICY_APPROVED)
        
  # public 
  def disapprove(self):
    self.policies_rm(POLICY_APPROVED)
    return str(self.id)
  
  # public
  def approve(self):
    self.policies_add(POLICY_APPROVED)
    return str(self.id)
  
  # public
  def get_profile(self):
    return self.profile if None != self.profile else {}
  
  # public
  def profile_updated(self, patch):
    return merger.merge(deepcopy(self.get_profile()), patch)
  
  # public
  def profile_update(self, *, patch, merge = True):
    # patch: Dict<string:path, Any>
    self.profile = self.profile_updated(patch) if merge else patch
    
  # public
  def is_archived(self):
    return self.includes_tags(TAG_ARCHIVED)
  
  # public
  def set_is_archived(self, flag = True):
    if flag:
      self.policies_add(TAG_ARCHIVED)
    else:
      self.policies_rm(TAG_ARCHIVED)

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
    
    return changes

  # public 
  def policies_rm(self, *policies):
    changes = 0

    for policy in filter(lambda p: self.includes_tags(p), policies):
      tp = Tags.by_name(policy, create = True)
      tp.users.remove(self)
      changes += 1
    
    if 0 < changes:
      db.session.commit()
    
    return changes
  
  # policies, batch-add-rm
  def policies_patch(self, policies):
    changes = 0
    changes += self.policies_add(
      *[pname for pname, value in policies.items() if bool(value)])
    changes += self.policies_rm(
      *[pname for pname, value in policies.items() if not bool(value)])
    return changes
    
  @staticmethod
  def clear_storage(uid):
    directory = os.path.join(UPLOAD_PATH.rstrip("/\\"), UPLOAD_DIR, str(uid))
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
  def create_user(*, email, password, 
                policies = DEFAULT_USER_CREATE_POLICIES):
    u = Users(
      email    = email,
      password = hashPassword(password)
    )

    db.session.add(u)
    db.session.commit()

    # add default policies
    u.policies_add(*policies)

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
      db.select(
        func.count(Users.id)
      ).where(
        email == Users.email))

  @staticmethod
  def by_uids(*uids):
    return db.session.scalars(
      db.select(
        Users
      ).where(
        Users.id.in_(uids)
      )
    )
  
