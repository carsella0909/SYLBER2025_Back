from datetime import datetime, timedelta
from json import loads

from fastapi import HTTPException
from fastapi.params import Security
from fastapi.security import APIKeyHeader
from jose import jwt

from models import session, User

CONFIG = loads(open("config.json").read())

JWT_CONFIG = CONFIG["jwt"]


def create_token(data: dict):
    expire = datetime.now() + timedelta(minutes=JWT_CONFIG["ACCESS_TOKEN_EXPIRE_MINUTES"])
    to_encode = data.copy()
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, JWT_CONFIG["SECRET_KEY"], algorithm=JWT_CONFIG["ALGORITHM"])
    return token


def decode_token(token: str):
    try:
        payload = jwt.decode(token, JWT_CONFIG["SECRET_KEY"], algorithms=[JWT_CONFIG["ALGORITHM"]])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")



def get_user(authorization: str = Security(APIKeyHeader(name="Authorization"))) -> User:
    try:
        token_type, token = authorization.split()
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid token")
    if token_type != "Bearer":
        raise HTTPException(status_code=401, detail="Invalid token type")
    try:
        payload = decode_token(token)
    except HTTPException as e:
        raise e
    user = session.query(User).filter(User.username == payload.get("sub")).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

def get_user_by_name(authorization: str = Security(APIKeyHeader(name="Authorization"))) -> str:
    try:
        token_type, token = authorization.split()
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid token")
    if token_type != "Bearer":
        raise HTTPException(status_code=401, detail="Invalid token type")
    try:
        payload = decode_token(token)
    except HTTPException as e:
        raise e
    return payload.get("sub")
