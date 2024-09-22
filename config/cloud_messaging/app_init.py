import firebase_admin
from firebase_admin import credentials

from flask_app import CLOUD_MESSAGING_CERTIFICATE


# service account key file
cert = credentials.Certificate(f'./{CLOUD_MESSAGING_CERTIFICATE}')

# Initialize the Firebase app
firebase_admin.initialize_app(cert)

