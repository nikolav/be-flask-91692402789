
def job():
  with open('./log.demo.txt', 'a') as file:
    file.write('demo_cronjob_2\n')

demo_cronjob_2 = {
  'id'      : 'demo_cronjob_2', 
  'trigger' : 'cron', 
  'func'    : job, 
  'minute'  : '*',
}

