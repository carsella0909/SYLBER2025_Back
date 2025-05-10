from typing import Annotated

from bcrypt import hashpw, gensalt, checkpw
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, HTTPBearer

from auth.token import create_token, get_user, get_user_by_name
from models import User, session

security = HTTPBearer()

router = APIRouter(
    prefix="/auth",
    tags=["users"],
)

@router.get("/me")
async def read_users_me(user: Annotated[User, Depends(get_user)]):
    return {
        "username": user.username,
    }

@router.put("/")
async def update_user(username: Annotated[str, Depends(get_user_by_name)],
                      password: str = None):
    user = session.query(User).filter(User.username == username).first()
    if password:
        user.password = hashpw(password.encode('utf-8'), gensalt()).decode("utf-8")
    try:
        session.commit()
        session.refresh(user)
    except Exception as e:
        print(e)
        session.rollback()
        raise HTTPException(status_code=400, detail="Error updating user")
    return {"message": "User updated successfully"}

@router.delete("/")
async def delete_user(username: Annotated[str, Depends(get_user_by_name)]):
    try:
        user = session.query(User).filter(User.username == username).first()
        session.delete(user)
        session.commit()
    except Exception as e:
        print(e)
        session.rollback()
        raise HTTPException(status_code=400, detail="Error deleting user")
    return {"message": "User deleted successfully"}

@router.post("/")
async def register(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        user = User(
            username=form_data.username,
            password=hashpw(form_data.password.encode('utf-8'), gensalt()).decode("utf-8"),
        )
        session.add(user)
        session.commit()
        session.refresh(user)
    except Exception as e:
        print(e)
        session.rollback()
        raise HTTPException(status_code=400, detail="name already exists")
    return {"message": "User created successfully"}

@router.get("/{username}")
async def get_user_info(username: str):
    user = session.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"username": user.username}

@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = session.query(User).filter(User.username == form_data.username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not checkpw(form_data.password.encode('utf-8'), user.password.encode('utf-8')):
        raise HTTPException(status_code=401, detail="Invalid password")
    token = create_token({"sub": user.username})
    return {
        "access_token": token,
        "token_type": "bearer"
    }
