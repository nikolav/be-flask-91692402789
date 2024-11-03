from sqlalchemy.orm import DeclarativeBase

# reexport classes from .package
from .response_status import ResponseStatus


class Base(DeclarativeBase):
  pass

