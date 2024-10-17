from flask      import Blueprint
from flask_cors import CORS

bp_testing = Blueprint('testing', __name__, url_prefix = '/test')

# cors blueprints as wel for cross-domain requests
CORS(bp_testing)


@bp_testing.route('/', methods = ('POST',))
def testing_home():     
  import io
  import requests
  from pprint import pprint
  # from flask import send_file
  import base64

  r = { 'error': None, 'status': None }
  file = None
  url = 'https://firebasestorage.googleapis.com/v0/b/jfejcxjyujx.appspot.com/o/media%2FASSETS%3AZJYH3%2Fimages%2F66%2Fproduct02.jpg?alt=media&token=cbc973d9-bc4d-46bd-8272-9b026f6fc528'
  filename = 'foo'
  try:
    response = requests.get(url)
    if 200 != response.status_code:
      raise Exception('--fetch-failed')
    file = io.BytesIO(response.content)
    # return send_file(file, 
    #                  download_name = filename)

  except Exception as err:
    r['error'] = str(err)
  
  
  else:
    r['status'] = { 'code' : response.status_code, 
                   'f'     : base64.b64encode(file.getvalue()).decode('utf-8')}
  # from flask import g
  # from servcies.firebase.messaging import send
  # from datetime import datetime
  # from datetime import timezone
  # send(
  #   tokens  = [
  #     'tok1',
  #     'tok2',
  #   ],
  #   payload = {'title': 'fcm:demo:3', 'body': str(datetime.now(tz = timezone.utc))}
  # )

  return r
