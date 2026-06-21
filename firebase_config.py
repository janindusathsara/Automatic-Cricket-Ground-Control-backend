"""
Firebase Realtime Database initialization and helper functions
Deprecated: Use utils.firebase_helper instead
"""

from utils.firebase_helper import FirebaseHelper

# For backward compatibility, expose FirebaseHelper as FirebaseDB
class FirebaseDB(FirebaseHelper):
    """Backward compatibility wrapper"""
    pass


# Initialize Firebase on import
try:
    FirebaseDB.initialize()
except Exception as e:
    print(f"Warning: Firebase initialization deferred - {str(e)}")
