import os

import firebase_admin
from firebase_admin import credentials


CLOUD_MESSAGING_CERTIFICATE = os.getenv('CLOUD_MESSAGING_CERTIFICATE')

# service account key file
creds = credentials.Certificate(f'./{CLOUD_MESSAGING_CERTIFICATE}')

# Initialize the Firebase app
app = firebase_admin.initialize_app(creds)
