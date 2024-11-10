
import random
import string

def id_gen(*, prefix = "", length = 5):
  '''
    Generate a random alphanumeric string of a given length.
  '''
  chars_random = ''.join(random.choices(string.ascii_letters + string.digits, k = length))
  return f'{prefix}:{chars_random}' if prefix else chars_random
