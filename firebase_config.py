"""
Firebase Realtime Database initialization and helper functions
"""

import firebase_admin
from firebase_admin import credentials, db
import json
import os
from config import Config


class FirebaseDB:
    """Firebase Realtime Database handler"""

    _initialized = False
    _db = None

    @classmethod
    def initialize(cls):
        """Initialize Firebase Admin SDK with environment variables"""
        if cls._initialized:
            return

        try:
            # Prepare private key - ensure it has PEM headers/footers
            private_key = Config.FIREBASE_PRIVATE_KEY
            if not private_key.startswith("-----BEGIN"):
                private_key = "-----BEGIN PRIVATE KEY-----\n" + private_key + "\n-----END PRIVATE KEY-----\n"
            
            # Create credentials dictionary from environment variables
            cred_dict = {
                "type": "service_account",
                "project_id": Config.FIREBASE_PROJECT_ID,
                "private_key_id": Config.FIREBASE_PRIVATE_KEY_ID,
                "private_key": private_key,
                "client_email": Config.FIREBASE_CLIENT_EMAIL,
                "client_id": Config.FIREBASE_CLIENT_ID,
                "auth_uri": Config.FIREBASE_AUTH_URI,
                "token_uri": Config.FIREBASE_TOKEN_URI,
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            }

            # Initialize Firebase Admin SDK
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(
                cred, {"databaseURL": Config.FIREBASE_DATABASE_URL}
            )

            cls._db = db
            cls._initialized = True
            print("✓ Firebase initialized successfully")

        except Exception as e:
            print(f"✗ Firebase initialization failed: {str(e)}")
            raise

    @classmethod
    def get_db(cls):
        """Get Firebase database reference"""
        if not cls._initialized:
            cls.initialize()
        return cls._db

    @classmethod
    def read(cls, path):
        """Read data from Firebase path"""
        try:
            ref = cls.get_db().reference(path)
            return ref.get().val() if ref.get() else None
        except Exception as e:
            print(f"✗ Error reading from Firebase: {str(e)}")
            return None

    @classmethod
    def write(cls, path, data):
        """Write data to Firebase path"""
        try:
            ref = cls.get_db().reference(path)
            ref.set(data)
            print(f"✓ Successfully wrote data to {path}")
            return True
        except Exception as e:
            print(f"✗ Error writing to Firebase: {str(e)}")
            return False

    @classmethod
    def update(cls, path, data):
        """Update data at Firebase path"""
        try:
            ref = cls.get_db().reference(path)
            ref.update(data)
            print(f"✓ Successfully updated data at {path}")
            return True
        except Exception as e:
            print(f"✗ Error updating Firebase: {str(e)}")
            return False

    @classmethod
    def delete(cls, path):
        """Delete data from Firebase path"""
        try:
            ref = cls.get_db().reference(path)
            ref.delete()
            print(f"✓ Successfully deleted data at {path}")
            return True
        except Exception as e:
            print(f"✗ Error deleting from Firebase: {str(e)}")
            return False


# Initialize Firebase on import
try:
    FirebaseDB.initialize()
except Exception as e:
    print(f"Warning: Firebase initialization deferred - {str(e)}")
