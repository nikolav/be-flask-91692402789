
def job():
  with open('./log.demo.txt', 'a') as file:
    file.write('demo_job_1:demo\n')

demo_job_1 = {
  'trigger' : 'interval', 
  'id'      : 'demo_job_1', 
  'func'    : job, 
  'seconds' : 5,
}

