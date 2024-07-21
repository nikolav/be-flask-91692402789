if __name__ == '__main__':    
  import os
  from flask_app import app
  from flask_app import io
  
  _port = os.getenv('PORT')

  io.run(app, 
          debug = True,
          host  = '0.0.0.0',
          port  = _port if None != _port else 5000,
          allow_unsafe_werkzeug = True,
        )
