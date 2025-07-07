from google.oauth2 import id_token
from google.auth.transport import requests

def verify_google_token(token):
    try:
        idinfo = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            audience=None  # Can be set to GOOGLE_CLIENT_ID to strictly validate
        )
        # ID token is valid. Return user's info
        return {
            "email": idinfo["email"],
            "name": idinfo.get("name", ""),
            "sub": idinfo["sub"]  # Google's user ID
        }
    except ValueError:
        return None
