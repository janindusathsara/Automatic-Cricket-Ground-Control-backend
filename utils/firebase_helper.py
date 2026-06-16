"""
Firebase Realtime Database Helper Functions
Centralized Firebase operations
"""

import firebase_admin
from firebase_admin import credentials, db
from config import Config
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class FirebaseHelper:
    """Helper class for Firebase operations"""

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
            try:
                cred = credentials.Certificate(cred_dict)
                firebase_admin.initialize_app(
                    cred, {"databaseURL": Config.FIREBASE_DATABASE_URL}
                )
            except ValueError:
                # App already initialized
                pass

            cls._db = db
            cls._initialized = True
            logger.info("✓ Firebase initialized successfully")

        except Exception as e:
            logger.error(f"✗ Firebase initialization failed: {str(e)}")
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
            data = ref.get()
            return data.val() if data else None
        except Exception as e:
            logger.error(f"✗ Error reading from Firebase {path}: {str(e)}")
            return None

    @classmethod
    def write(cls, path, data):
        """Write data to Firebase path"""
        try:
            ref = cls.get_db().reference(path)
            ref.set(data)
            logger.info(f"✓ Successfully wrote data to {path}")
            return True
        except Exception as e:
            logger.error(f"✗ Error writing to Firebase {path}: {str(e)}")
            return False

    @classmethod
    def update(cls, path, data):
        """Update data at Firebase path"""
        try:
            ref = cls.get_db().reference(path)
            ref.update(data)
            logger.info(f"✓ Successfully updated data at {path}")
            return True
        except Exception as e:
            logger.error(f"✗ Error updating Firebase {path}: {str(e)}")
            return False

    @classmethod
    def delete(cls, path):
        """Delete data from Firebase path"""
        try:
            ref = cls.get_db().reference(path)
            ref.delete()
            logger.info(f"✓ Successfully deleted data at {path}")
            return True
        except Exception as e:
            logger.error(f"✗ Error deleting from Firebase {path}: {str(e)}")
            return False

    @classmethod
    def get_server_timestamp(cls):
        """Get server timestamp"""
        return datetime.now().isoformat()
