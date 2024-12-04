
from datetime import datetime
from datetime import timedelta
# from datetime import timezone


def week_start(h = 0, m = 0, s = 0, ms = 0):
  today_ = datetime.now()
  ws_    = today_ - timedelta(days = today_.weekday())
  return ws_.replace(hour = h, minute = m, second = s, microsecond = ms)

def month_start(h = 0, m = 0, s = 0, ms = 0):
  d = datetime.now()
  return d.replace(day = 1, hour = h, minute = m, second = s, microsecond = ms)


