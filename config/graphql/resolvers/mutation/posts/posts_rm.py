import os

from flask     import g
from flask_app import db
from flask_app import io

from models.posts          import Posts
from config.graphql.init   import mutation
from schemas.serialization import SchemaSerializePosts

IOEVENT_POST_CHANGE_SINGLE_prefix = os.getenv('IOEVENT_POST_CHANGE_SINGLE_prefix')
IOEVENT_USER_POSTS_CHANGE_prefix  = os.getenv('IOEVENT_USER_POSTS_CHANGE_prefix')
IOEVENT_POSTS_CHANGE              = os.getenv('IOEVENT_POSTS_CHANGE')


# garbadge collects related doc-images when post is removed
# rm from `docs` where tag like `{POST_IMAGES_prefix}{postId}:`
# POST_IMAGES_prefix = os.getenv('POST_IMAGES_prefix')


@mutation.field('postsRemove')
def resolve_postsRemove(_obj, _info, id):
  p   = None
  uid = None

  try:
    p = db.session.get(Posts, id)

    # @forbidden raise
    if not p:
      raise Exception('forbidden')
    
    if not p.user.id == g.user.id:
      raise Exception('forbidden')
    
    # cache uid for io.emit
    #  `p.user` .user unavailable after post.delete
    uid = p.user.id
    
    g.user.posts.remove(p)
    db.session.delete(p)
    
    db.session.commit()

  except Exception as err:
    raise err

  else:

    if None != p.id:
      
      # post removed here, garbage collect related nodes
      #  check related attachments, images, docs, to remove
      #   then rm Tags related

      # rm post images
      p.drop_images()
      
      # get related file-docs to remove
      #  rm where tag like '{POST_IMAGES_prefix}{ppid}%'
      
      # @todo remove related docs-attachments    
    
    if None != p.id:
      # # emit updated
      io.emit(f'{IOEVENT_POST_CHANGE_SINGLE_prefix}{p.id}')
      io.emit(f'{IOEVENT_USER_POSTS_CHANGE_prefix}{uid}')
      io.emit(IOEVENT_POSTS_CHANGE)
  
  return SchemaSerializePosts().dump(p) if None != p else None
