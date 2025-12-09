from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt, JWTError
from pydantic import BaseModel

from config import get_settings


class User(BaseModel):
    sub: str
    email: Optional[str] = None


security = HTTPBearer(auto_error=True)


def verify_supabase_jwt(token: str) -> User:
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.supabase_jwt_secret, algorithms=["HS256"])
        sub = payload.get("sub") or payload.get("user_id")
        if not sub:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
        return User(sub=sub, email=payload.get("email"))
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


def auth_dependency(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    token = credentials.credentials
    return verify_supabase_jwt(token)

