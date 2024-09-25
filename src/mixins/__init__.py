from datetime import datetime
from datetime import timezone

from sqlalchemy     import func
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from flask_app import db


class MixinTimestamps():
  created_at: Mapped[datetime] = mapped_column(default = lambda: datetime.now(timezone.utc))
  updated_at: Mapped[datetime] = mapped_column(default = lambda: datetime.now(timezone.utc),
                                               onupdate = lambda: datetime.now(timezone.utc))

class MixinIncludesTags():
  # public
  def includes_tags(self, *args, ANY = False):
    tags_self = [t.tag for t in self.tags]
    return all(tag in tags_self for tag in args) if True != ANY else any(tag in tags_self for tag in args)


class MixinExistsID():
  @classmethod
  def id_exists(cls, id):
    return 0 < db.session.scalar(
      db.select(
        func.count(cls.id)
      ).where(
        id == cls.id
      )
    )
