import firebase_admin
from firebase_admin import credentials, auth, storage
from django.conf import settings
import os
import firebase_admin
from firebase_admin import credentials, auth, storage
from django.conf import settings
import os
import json

# Initialize Firebase Admin SDK
if hasattr(settings, 'FIREBASE_CREDENTIALS_JSON') and settings.FIREBASE_CREDENTIALS_JSON:
    # Production: Load from environment variable
    cred_dict = json.loads(settings.FIREBASE_CREDENTIALS_JSON)
    cred = credentials.Certificate(cred_dict)
else:
    # Development: Load from file
    cred_path = os.path.join(settings.BASE_DIR, 'firebase-credentials.json')
    cred = credentials.Certificate(cred_path)

firebase_admin.initialize_app(cred, {
    'storageBucket': 'clothmarket-de8e9.firebasestorage.app'  # Replace with your bucket
})



def verify_firebase_token(id_token):
    """Verify Firebase ID token"""
    try:
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token
    except Exception as e:
        return None

def upload_to_firebase_storage(file, path):
    """Upload file to Firebase Storage"""
    try:
        bucket = storage.bucket()
        blob = bucket.blob(path)
        blob.upload_from_file(file)
        blob.make_public()
        return blob.public_url
    except Exception as e:
        return None