
def job():
  with open('./log.demo.txt', 'a') as file:
    file.write('demo_cronjob_2\n')

demo_cronjob_2 = {
  'trigger' : 'cron', 
  'id'      : 'demo_cronjob_2', 
  'func'    : job, 
  'minute'  : '*',
}

