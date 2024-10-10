import re
import secrets
import string
from random         import randbytes
from functools      import reduce
from werkzeug.utils import secure_filename



re_base_ext = r'(.*)\.([^\.]+)'

id_gen = lambda: randbytes(4).hex()

def gen_filename(filename, file_id):
  f_base, f_ext = re.match(re_base_ext, filename).groups()
  return secure_filename(f'{f_base}.{file_id}.{f_ext}')


class Lists():
  @staticmethod
  def intersection(*lists):
    return reduce(set.intersection, map(set, lists))

class Unique():
  @staticmethod
  def id(*, length = 5):
    alpha = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alpha) for _ in range(length))
