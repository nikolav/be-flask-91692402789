import secrets

def hex_rand():
  return secrets.token_bytes().hex()
