import os
import requests

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

def get_google_auth_url():
    return (
        "https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={GOOGLE_CLIENT_ID}&"
        "redirect_uri=http://localhost:8000/auth/callback&"
        "response_type=code&"
        "scope=https://www.googleapis.com/auth/gmail.readonly https://www.googleapis.com/auth/userinfo.email&"
        "access_type=offline"
    )

def exchange_code_for_tokens(code: str):
    url = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": "http://localhost:8000/auth/callback",
        "grant_type": "authorization_code"
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    res = requests.post(url, data=data, headers=headers)
    return res.json()
