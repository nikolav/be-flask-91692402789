# SCHEDULER_API_ENABLED: bool (default: False)
# SCHEDULER_API_PREFIX: str (default: "/scheduler")
# SCHEDULER_ENDPOINT_PREFIX: str (default: "scheduler.")
# SCHEDULER_ALLOWED_HOSTS: list (default: ["*"])

from flask_apscheduler import APScheduler

from jobs import JOBS


class Config:
  SCHEDULER_API_ENABLED = False
  JOBS = JOBS

scheduler_config = Config()
scheduler        = APScheduler()

def scheduler_configure(app, *, start = True):
  app.config.from_object(scheduler_config)
  scheduler.init_app(app)
  
  if True == start:
    scheduler.start()

