import bcrypt
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.config import settings
from app.database import get_db
from app import models

# OAuth2 Scheme for Bearer Token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not plain_password or not hashed_password:
        return False
    
    try:
        if hashed_password.startswith("$2"):
            p_bytes = plain_password.encode('utf-8')[:72]
            h_bytes = hashed_password.encode('utf-8')
            if bcrypt.checkpw(p_bytes, h_bytes):
                return True
            
            # Check stripped password if space was inadvertently added
            p_stripped = plain_password.strip().encode('utf-8')[:72]
            if p_stripped != p_bytes and bcrypt.checkpw(p_stripped, h_bytes):
                return True
            return False
        
        return plain_password == hashed_password or plain_password.strip() == hashed_password
    except Exception as e:
        print(f"[VERIFY PASSWORD ERROR] {e}")
        return False

def get_password_hash(password: str) -> str:
    password_bytes = password.strip().encode('utf-8')[:72]
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "sub": str(data.get("sub"))})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt

def get_current_learner(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> models.Learner:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials or token expired",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        sub_val = payload.get("sub")
        if sub_val is None:
            raise credentials_exception
        learner_id = int(sub_val)
    except (JWTError, ValueError):
        raise credentials_exception

    learner = db.query(models.Learner).filter(models.Learner.learner_id == learner_id).first()
    if learner is None:
        raise credentials_exception

    return learner

def get_optional_current_learner(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> Optional[models.Learner]:
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        sub_val = payload.get("sub")
        if sub_val is None:
            return None
        learner_id = int(sub_val)
        return db.query(models.Learner).filter(models.Learner.learner_id == learner_id).first()
    except Exception:
        return None
