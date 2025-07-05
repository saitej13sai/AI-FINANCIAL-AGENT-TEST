# backend/routers/auth.py

from fastapi import APIRouter, Request
from utils.auth import get_google_auth_url, exchange_code_for_tokens

router = APIRouter()


@router.get("/auth/url")
def generate_auth_url():
    return {"auth_url": get_google_auth_url()}


@router.get("/auth/callback")
async def auth_callback(request: Request):
    code = request.query_params.get("code")
    if not code:
        return {"error": "Missing code in query parameters"}
    
    try:
        tokens = exchange_code_for_tokens(code)
        return {"message": "Token exchange successful", "tokens": tokens}
    except Exception as e:
        return {"error": str(e)}

