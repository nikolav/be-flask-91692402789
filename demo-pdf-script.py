import base64

from selenium import webdriver
from selenium.webdriver.chrome.service import Service


# load html in headless chrome
data    = '<a href="https://nikolav.rs/">@nikolav.rs</a>'
b64data = base64.b64encode(data.encode('utf-8')).decode('utf-8')
uridata = f'data:text/html;base64,{b64data}'

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--disable-infobars')
chrome_options.add_argument('--disable-extensions')
chrome_options.add_argument('--disable-popup-blocking')
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

service = Service()
driver  = webdriver.Chrome(
  service = service, 
  options = chrome_options)

driver.get(uridata)

params = { 
  'printBackground' : True ,
  'landscape'       : False,
  'paperWidth'      : 8.26,
  'paperHeight'     : 11.68,
}
pdfdata = driver.execute_cdp_cmd("Page.printToPDF",  params)

pdf = base64.b64decode(pdfdata['data'])

with open('out.pdf', 'wb') as f:
  f.write(pdf)

driver.quit()

