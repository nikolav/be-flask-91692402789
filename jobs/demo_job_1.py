
def job():
  with open('./log.demo.txt', 'a') as file:
    file.write('demo_job_1\n')

demo_job_1 = {
  'id'      : 'demo_job_1', 
  'trigger' : 'interval', 
  'func'    : job, 
  'seconds' : 5,
}

