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
from sqlalchemy.orm import backref

from . import db
from . import usersTable
from . import ln_users_tags
from . import ln_users_assets
from . import ln_users_users_follow
from . import ln_users_users_manage
from src.mixins import MixinTimestamps
from src.mixins import MixinIncludesTags
from src.mixins import MixinByIds
from src.mixins import MixinFieldMergeable

from models.tags     import Tags
from models.docs     import Docs
from models.assets   import Assets
from models.assets   import AssetsType

# from utils.str import match_after_last_at
from utils.pw  import hash as hashPassword

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
from flask_app import POLICY_ALL

from schemas.serialization import SchemaSerializeUsersTextSearch
from config                import skip_list_users

from utils.id_gen import id_gen


# https://help.zoho.com/galleryDocuments/edbsne9896a615107dc695c0c42640947c15396f645651fa8eb1ae6632e434ba6231388ce5ff6e47742393c1b76377ff36fff?inline=true
class UsersTagsStatus(Enum):
  AVAILABLE      = 'AVAILABLE:vmWsUhVctBpu1BAp'
  AWAY           = 'AWAY:p2oLyHH'
  BUSY           = 'BUSY:woxs5B8Slw'
  DO_NOT_DISTURB = 'DO_NOT_DISTURB:eb6Y5nXzlK'
  INVISIBLE      = 'INVISIBLE:EDjVu'


class UsersPolicies(Enum):
  APPROVED    = POLICY_APPROVED
  ADMINS      = POLICY_ADMINS
  EMAIL       = POLICY_EMAIL
  FILESTORAGE = POLICY_FILESTORAGE
  MANAGERS    = POLICY_MANAGERS
  EXTERNAL    = TAG_USERS_EXTERNAL
  MESSAGING   = '@policy:MESSAGING:tyULfGCZSQ9s7gGH'
  ALL         = POLICY_ALL


DEFAULT_USER_CREATE_POLICIES = (
  POLICY_APPROVED, 
  POLICY_EMAIL, 
  POLICY_FILESTORAGE,
  UsersPolicies.MESSAGING.value,
)

  

class Users(MixinTimestamps, MixinIncludesTags, MixinByIds, MixinFieldMergeable, db.Model):
  __tablename__ = usersTable
  
  id: Mapped[int] = mapped_column(primary_key = True)
  
  email    : Mapped[str] = mapped_column(unique = True)
  password : Mapped[str]
  profile  : Mapped[Optional[dict]] = mapped_column(JSON)
  # assign key:string @create
  key: Mapped[Optional[str]] = mapped_column(default = id_gen)
  
  # virtual
  tags         : Mapped[List['Tags']]     = relationship(secondary = ln_users_tags, back_populates = 'users')
  docs         : Mapped[List['Docs']]     = relationship(back_populates = 'user')
  assets       : Mapped[List['Assets']]   = relationship(secondary = ln_users_assets, back_populates = 'users')
  assets_owned : Mapped[List['Assets']]   = relationship(back_populates = 'author') # assets created by the user
  orders       : Mapped[List['Orders']]   = relationship(back_populates = 'author') # orders created by the user

  # self-referential, has|belongs-to assets
  users_following: Mapped[List['Users']] = relationship(
    secondary      = ln_users_users_follow, 
    primaryjoin    = id == ln_users_users_follow.c.users_l_id, 
    secondaryjoin  = id == ln_users_users_follow.c.users_r_id, 
    backref        = backref( 'users_followers', lazy='dynamic')
    # back_populates = 'assets'
  )

  # self-referential, has|belongs-to assets
  users_managing: Mapped[List['Users']] = relationship(
    secondary      = ln_users_users_manage, 
    primaryjoin    = id == ln_users_users_manage.c.users_l_id, 
    secondaryjoin  = id == ln_users_users_manage.c.users_r_id, 
    backref        = backref( 'users_managers', lazy='dynamic')
    # back_populates = 'assets'
  )


  # magic
  def __repr__(self):
    return f'<Users(id={self.id!r}, email={self.email!r})>'
  
  # public
  def is_default_user(self):
    return Users.is_default(self.id)
  
  # public
  def serialize_to_text_search(self):
    return ' '.join(v for v in SchemaSerializeUsersTextSearch().dump(self).values() if v).lower()
  
  def related_assets(self, *, TYPE = None, DISTINCT = True, PtAIDS = None, WITH_OWN = True):
    return Assets.assets_parents(*self.groups(), PtAIDS = PtAIDS,
                                 TYPE = TYPE, DISTINCT = DISTINCT, WITH_OWN = WITH_OWN)

  def related_assets_sites_managed(self, *, PtAIDS = None, WITH_OWN = True):
    return self.related_assets(TYPE = AssetsType.PHYSICAL_STORE.value, 
                               PtAIDS = PtAIDS, WITH_OWN = WITH_OWN)
  
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
    d = Docs.users_availabilities()
    p = d.dataField_updated(patch = { str(self.id): value })
    d.dataField_update(patch = p)
    db.session.commit()
  
  # public
  def availability_is(self, value):
    d = Docs.users_availabilities()
    return value == d.data.get(str(self.id))

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
      return [k_tok for k_tok, k_val in dt.data.items() if True == k_val]

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
        self.id == Users.id))
  
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
    return self.dataField_updated(patch = patch, FIELD = 'profile')
  
  # public
  def profile_update(self, *, patch, merge = True):
    # patch: Dict<string:path, Any>
    # self.profile = self.profile_updated(patch) if merge else patch
    patched = self.profile_updated(patch) if merge else patch
    self.dataField_update(patch = patched, FIELD = 'profile')
    
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
  def policies_add(self, *policies, _commit = True):
    changes = 0

    for policy in filter(lambda p: not self.includes_tags(p), policies):
      tp = Tags.by_name(policy, create = True, _commit = _commit)
      tp.users.append(self)
      changes += 1
    
    if (0 < changes) and (True == _commit):
      db.session.commit()
    
    return changes

  # public 
  def policies_rm(self, *policies, _commit = True):
    changes = 0

    for policy in filter(lambda p: self.includes_tags(p), policies):
      tp = Tags.by_name(policy, create = True, _commit = _commit)
      tp.users.remove(self)
      changes += 1
    
    if (0 < changes) and (True == _commit):
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
  def list_all_safe():
    return db.session.scalars(
      db.select(
        Users
      ).where(
        ~Users.id.in_(skip_list_users)
      ))
    
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
                  policies = []):
    u = Users(
      email    = email,
      password = hashPassword(password)
    )

    db.session.add(u)
    db.session.commit()

    # add default policies
    u.policies_add(*DEFAULT_USER_CREATE_POLICIES, *policies)

    return u

  @staticmethod
  def is_default(id):
    try:
      return id == db.session.scalar(
        db.select(
          Users.id
        ).where(
          USER_EMAIL == Users.email
        ))
    
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
    return Users.by_ids(*uids)
  
