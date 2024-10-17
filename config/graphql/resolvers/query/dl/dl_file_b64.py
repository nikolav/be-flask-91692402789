import io
import requests
import base64

from config.graphql.init import query

from marshmallow import Schema
from marshmallow import fields


class SchemaFileUrl(Schema):
  url = fields.Url(required = True)

@query.field('dlFileB64')
def resolve_dlFileB64(_obj, _info, data):
  r     = { 'error': None, 'status': None }
  file  = None
  fdata = None

  try:
    url = SchemaFileUrl().load(data).get('url')

    response = requests.get(url)
    if 200 != response.status_code:
      raise Exception('--FETCH-failed')

    file  = io.BytesIO(response.content)
    fdata = base64.b64encode(file.getvalue()).decode('utf-8')

  
  except Exception as err:
    r['error'] = str(err)
  
  
  else:
    r['status'] = { 'data': fdata }


  return r

