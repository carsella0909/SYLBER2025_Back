import random
from random import shuffle
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer

from auth.token import  get_user
from models import *
from auth.token import  get_user
from models import *

from pydantic import BaseModel

import os

# make me a class for post which is wav record file
class Audio(BaseModel):
    audio: bytes
    round: int

# make me a class for post which is text

class Text(BaseModel):
    text: str
    round: int

security = HTTPBearer()

router = APIRouter(
    prefix="/room",
    tags=["rooms"],
)


@router.get("/")
async def create_room(user: Annotated[User, Depends(get_user)],
                       max_users: int = 8):
    # check if user is already in any room
    roomuser = session.query(RoomUser).filter(RoomUser.user_id == user.id).first()
    if roomuser:
        raise HTTPException(status_code=400, detail="User is already in a room")

    characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    code = "".join(characters[random.randint(0, len(characters) - 1)] for _ in range(5))
    # Check if code is already in use and generate a new one if it is
    while session.query(Room).filter(Room.code == code).first():
        code = "".join(characters[random.randint(0, len(characters) - 1)] for _ in range(5))

    room = Room(
        max_users=max_users,
        code=code,
        status = "active",
        host_id=user.id,
    )
    session.add(room)
    room.join(user)
    session.commit()
    session.refresh(room)
    return {
        "id": room.id,
        "max_users": room.max_users,
        "code": room.code,
        "status": room.status,
        "created_at": room.created_at,
        "host_id": room.host_id,
    }


@router.get("/{code}")
async def get_room(user: Annotated[User, Depends(get_user)],code: str):
    room = session.query(Room).filter(Room.code == code).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    if room.status == "inactive":
        raise HTTPException(status_code=400, detail="Room is not active")
    if room.status == "playing":
        raise HTTPException(status_code=400, detail="Room is already playing")
    # return users in room with sort by entered_at
    users = session.query(User).filter(User.id == RoomUser.user_id).filter(RoomUser.room_id == room.id).order_by(RoomUser.entered_at).all()
    if not users:
        raise HTTPException(status_code=404, detail="No users in room")
    user_check = session.query(RoomUser).filter(user.id == RoomUser.user_id).filter(RoomUser.room_id == room.id).first()
    if not user_check:
        raise HTTPException(status_code=404, detail="No permission to view room")

    return {
        "id": room.id,
        "max_users": room.max_users,
        "code": room.code,
        "status": room.status,
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
    if room.status == "inactive":
        raise HTTPException(status_code=400, detail="Room is not active")
    if room.status == "playing":
        raise HTTPException(status_code=400, detail="Room is already playing")
    # check if user is already in any room
    roomuser = session.query(RoomUser).filter(RoomUser.user_id == user.id).first()
    if roomuser:
        raise HTTPException(status_code=400, detail="User is already in a room")
    if room.max_users <= len(room.room_users):
        raise HTTPException(status_code=400, detail="Room is full")
    room.join(user)
    return {
        "id": room.id,
        "max_users": room.max_users,
        "code": room.code,
        "status": room.status,
        "created_at": room.created_at,
        "host_id": room.host_id,
    }

@router.get("/leave/{code}")
async def leave_room(user: Annotated[User, Depends(get_user)],
                      code: str):
    room = session.query(Room).filter(Room.code == code).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    if room.status == "inactive":
        raise HTTPException(status_code=400, detail="Room is not active")
    if room.status == "playing":
        raise HTTPException(status_code=400, detail="Room is already playing")
    if user.id == room.host_id:
        room.delete()
    else:
        room.leave(user)
    # check if room is empty
    roomusers = session.query(RoomUser).filter(RoomUser.room_id == room.id).all()
    if not roomusers:
        room.delete()
    return {
        "id": room.id,
        "max_users": room.max_users,
        "code": room.code,
        "status": room.status,
        "created_at": room.created_at,
        "host_id": room.host_id,
    }

def get_game(user, room) -> Game:
    game = session.query(Game).join(
        Room, Game.room_id == Room.id
    ).join(
        RoomUser, RoomUser.room_id == Room.id
    ).filter(
        RoomUser.user_id == user.id,
        RoomUser.room_id == room.id,
        Room.status == "playing",
        Game.room_id == room.id,
    ).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    return game


@router.get("/{code}/start")
async def start_game(user: Annotated[User, Depends(get_user)], code: str):
    room = session.query(Room).filter(Room.code == code).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    if room.status == "inactive":
        raise HTTPException(status_code=400, detail="Room is not active")
    if room.status == "playing":
        raise HTTPException(status_code=400, detail="Room is already playing")
    if user.id != room.host_id:
        raise HTTPException(status_code=403, detail="Only host can start the game")
    # check if there are enough users in the room
    if len(room.room_users) < 2:
        raise HTTPException(status_code=400, detail="Not enough users in the room")
    # start game
    room.status = "playing"
    session.commit()
    game = Game(
        room_id=room.id,
    )
    session.add(game)
    session.commit()
    session.refresh(game)
    users = session.query(User).filter(User.id == RoomUser.user_id).filter(RoomUser.room_id == room.id).all()
    shuffle(users)
    contents = []
    for r in range(1, len(users)+1):
        round = Round(
            game_id=game.id,
            round=r,
            started_at=datetime.now() + timedelta(seconds=game.time_limit * (r-1)),
            type = "text" if r % 2 == 1 else "audio",
        )
        session.add(round)
        session.commit()
        session.refresh(round)
        contents.append([])
        for i, u in enumerate(users):
            content = Content(
                round_id=round.game_id,
                user_id=u.id,
                content = None,
                prev_content_id = None if r == 1 else contents[r-2][(i+1) % len(users)].id,
            )
            session.add(content)
            session.commit()
            session.refresh(content)
            contents[r-1].append(content)
        return

@router.get("/{code}/round")
async def get_round_data(user: Annotated[User, Depends(get_user)], code: str):
    room = session.query(Room).filter(Room.code == code).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    if room.status == "inactive":
        raise HTTPException(status_code=400, detail="Room is not active")
    if room.status == "playing":
        raise HTTPException(status_code=400, detail="Room is already playing")
    game = get_game(user, room)
    # get current round by started at and time limit
    round = session.query(Round).filter(
        Round.game_id == game.id,
        Round.started_at <= datetime.now(),
        Round.started_at + timedelta(seconds=game.time_limit) >= datetime.now(),
    ).first()
    if not round:
        raise HTTPException(status_code=404, detail="Round not found")
    # return round(int), number of left people, times left
    not_null_content_count = session.query(Round).filter(
        Round.game_id == game.id,
        Content.content != None
    ).count()
    return {
        "round": round.round,
        "left_people": len(room.room_users) - not_null_content_count,
        "time_left": game.time_limit - (datetime.now() - round.started_at).seconds,
    }

@router.get("/{code}/result")
async def end_game(user: Annotated[User, Depends(get_user)], code: str):
    room = session.query(Room).filter(Room.code == code).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    game = session.query(Game).join(
        Room, Game.room_id == Room.id
    ).filter(
        Room.code == code,
        Room.status == "inactive"
    )
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    # send all contents related to this game sorted by user, round
    contents = session.query(Content).join(
        Round, Content.round_id == Round.game_id
    ).join(
        Game, Round.game_id == Game.id
    ).filter(
        Game.id == game.id,
        Content.round_id == Round.game_id,
    ).all()
    # check if there are contents
    if not contents:
        raise HTTPException(status_code=404, detail="No contents found")

    return {
        "game_id": game.id,
        "contents": [
            {
                "id": content.id,
                "user_id": content.user_id,
                "round": content.round.round,
                "content": content.content,
                "prev_content_id": content.prev_content_id,
            }
            for content in contents
        ]
    }

    # return contents connected by prev_content_id

@router.get("/{code}/next")
async def what_is_next(user: Annotated[User, Depends(get_user)], code: str):
    room = session.query(Room).filter(Room.code == code).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    match room.status:
        case "inactive":
            return "end"
        case "active":
            return "waiting"
        case "playing":
            #round, time left, human done
            game = get_game(user, room)
            # get current round
            round = session.query(Round).filter(
                Round.game_id == game.id,
                Round.started_at <= datetime.now(),
                Round.started_at + timedelta(seconds=game.time_limit) >= datetime.now(),
            ).first()
            if not round:
                room.status = "inactive"
                session.commit()
                return "end"
            # get not null current content
            not_null_content = session.query(Content).filter(
                Content.round_id == round.id,
                Content.content != None
            ).count()
            return {
                "round": round.round,
                "time_left": game.time_limit - (datetime.now() - round.started_at).seconds,
                "user_done": not_null_content,
            }

@router.post("/{code}/answer")
async def answer_question(user: Annotated[User, Depends(get_user)], code: str, data: Text|Audio):
    room = session.query(Room).filter(Room.code == code).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    if room.status == "inactive":
        raise HTTPException(status_code=400, detail="Room is not active")
    if room.status == "active":
        raise HTTPException(status_code=400, detail="Room is not playing")
    game = get_game(user, room)
    # get latest round
    round = session.query(Round).filter(Round.game_id == game.id).order_by(Round.round.desc()).first()
    if not round:
        raise HTTPException(status_code=404, detail="Round not found")
    if round.round != data.round:
        raise HTTPException(status_code=400, detail="Round not found")
    # check if user already answered this round
    content = session.query(Content).filter(Content.user_id == user.id, Content.round == data.round).first()
    if content:
        raise HTTPException(status_code=400, detail="User already answered this round")
    # check if round is ended
    if round.is_ended():
        raise HTTPException(status_code=400, detail="Round is ended")
    # check if round is audio or text
    if round.type == "text":
        content = Content(
            user_id=user.id,
            round_id = round.id,
            content=data.text
        )
    elif round.type == "audio":
        # save data(audio file) in tmp/{round_id}_{user_id}.wav

        file_path = f"tmp/{round.id}_{user.id}.wav"
        os.makedirs("tmp", exist_ok=True)
        with open(file_path, "wb") as f:
            f.write(data.audio)

        content = Content(
            user_id=user.id,
            round_id = round.id,
            content=file_path
        )