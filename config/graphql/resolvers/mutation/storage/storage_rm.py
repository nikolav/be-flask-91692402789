import os

from flask import g

from flask_app import db
from flask_app import io
from flask_app import TAG_STORAGE
from flask_app import POLICY_FILESTORAGE

from middleware.authguard import authguard
from config.graphql.init  import mutation
from models.tags          import Tags

from utils.doc_json_date import docJsonDates as doc_plain


@mutation.field('storageRemoveFile')
@authguard(POLICY_FILESTORAGE)
def resolve_storageRemoveFile(_obj, _info, file_id):
  print(f'remove: file_id [{file_id}]')
  # try
  #  file exists
  #   unlink
  #    rm data @db
  #     @200, file deleted, io:change

  r = { 'error': None, 'file': None }
  
  tag_storage_ = f'{TAG_STORAGE}{g.user.id}'
  doc_file     = None


  try:
    # get related file Docs{}
    tag = Tags.by_name(tag_storage_, create = True)
    for doc in tag.docs:
      if file_id == doc.data['file_id']:
        doc_file = doc
        break
    
    if not doc_file:
      raise Exception('file not found')
    
    if not os.path.exists(doc_file.data['path']):
      raise Exception('no file')
    
    os.unlink(doc_file.data['path'])

    if os.path.exists(doc_file.data['path']):
      raise Exception('file.remove failed')
    
    tag.docs.remove(doc_file)
    db.session.delete(doc_file)
    
    db.session.commit()
    
    
  except Exception as err:
    r['error'] = str(err)
    
  
  else:    
    # @200, file deleted
    r['file'] = doc_plain(doc_file)
    io.emit(tag_storage_)
  
  
  return r

