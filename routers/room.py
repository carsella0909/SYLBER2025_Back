from typing import Annotated

from bcrypt import hashpw, gensalt, checkpw
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, HTTPBearer

from auth.token import create_token, get_user, get_user_by_name
from models import User, Room, session, RoomUser

security = HTTPBearer()

router = APIRouter(
    prefix="/room",
    tags=["rooms"],
)

@router.get("/")
async def create_room(user: Annotated[User, Depends(get_user)],
                       max_users: int = 8):
    room = Room(
        max_users=max_users,
        code="",
        is_active=True,
        host_id=user.id,
    )
    session.add(room)
    session.commit()
    session.refresh(room)
    return {
        "id": room.id,
        "max_users": room.max_users,
        "code": room.code,
        "is_active": room.is_active,
        "created_at": room.created_at,
        "host_id": room.host_id,
    }

@router.get("/{code}")
async def get_room(code: str):
    room = session.query(Room).filter(Room.code == code).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    # return users in room with sort by entered_at
    users = session.query(RoomUser).filter(RoomUser.room_id == room.id).order_by(RoomUser.entered_at).all()
    if not users:
        raise HTTPException(status_code=404, detail="No users in room")
    return {
        "id": room.id,
        "max_users": room.max_users,
        "code": room.code,
        "is_active": room.is_active,
        "created_at": room.created_at,
        "host_id": room.host_id,
        "users": [
            {
                "id": user.id,
                "username": user.username,
            }
            for user in users
        ],
    }

@router.get("/join/{code}")
async def join_room(user: Annotated[User, Depends(get_user)],
                     code: str):
    room = session.query(Room).filter(Room.code == code).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    # check if user is already in any room
    roomuser = session.query(RoomUser).filter(RoomUser.user_id == user.id).first()
    if roomuser:
        raise HTTPException(status_code=400, detail="User is already in a room")
    if room.max_users <= len(room.room_users):
        raise HTTPException(status_code=400, detail="Room is full")
    room.join(user.id)
    return {
        "id": room.id,
        "max_users": room.max_users,
        "code": room.code,
        "is_active": room.is_active,
        "created_at": room.created_at,
        "host_id": room.host_id,
    }

@router.get("/leave/{code}")
async def leave_room(user: Annotated[User, Depends(get_user)],
                      code: str):
    room = session.query(Room).filter(Room.code == code).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    if user.id == room.host_id:
        room.delete()
    else:
        room.leave(user.id)
    # check if room is empty
    if not room.roomusers:
        room.is_active = False
    return {
        "id": room.id,
        "max_users": room.max_users,
        "code": room.code,
        "is_active": room.is_active,
        "created_at": room.created_at,
        "host_id": room.host_id,
    }
