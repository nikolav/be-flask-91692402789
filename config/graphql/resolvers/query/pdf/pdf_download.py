
import base64

from flask  import render_template

from config.graphql.init import query
from src.services.pdf    import printHtmlToPDF


def render_template_blank_a4(data):
  return render_template('pdf/blank-a4.html', content = data.get('content'))

TEMPLATE = {
  'blank-a4': render_template_blank_a4,
}


@query.field('pdfDownload')
def resolve_pdfDownload(_obj, _info, data):
  # file = BytesIO(printHtmlToPDF(document_from_request_data_to_render()))
  # return send_file(file,
  #   as_attachment = True,
  #   download_name = 'download.pdf',
  #   mimetype      = 'application/pdf',
  # )

  template_name = data.get('template')
  file = printHtmlToPDF(TEMPLATE[template_name](data))
  return base64.b64encode(file).decode('utf-8')

