from json import loads

from fastapi import HTTPException
from sqlalchemy import create_engine, ForeignKey, UUID, PrimaryKeyConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session, relationship
from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP
from sqlalchemy.sql.functions import current_timestamp

CONFIG = loads(open("config.json").read())
DATABASE_URL = CONFIG["database"]["url"]
engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = scoped_session(SessionLocal)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(UUID, primary_key=True, index=True, server_default="uuid_generate_v4()")
    username = Column(String, unique=True, index=True)
    password = Column(String, nullable=False)

class RoomUser(Base):
    __tablename__ = "room_users"

    room_id = Column(Integer, ForeignKey("rooms.id"), primary_key=True)
    room = relationship("Room", backref="room_users")
    user_id = Column(UUID, ForeignKey("users.id"), primary_key=True)
    user = relationship("User", backref="room_users")
    is_connected = Column(Boolean, nullable=False, default=True)
    entered_at = Column(TIMESTAMP, nullable=False, default = current_timestamp())
    sid = Column(String, nullable=True)
    # use (room_id, user_id) as primary key
    __table_args__ = (
        PrimaryKeyConstraint('room_id', 'user_id'),
    )


class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    max_users = Column(Integer, nullable=False, default=8)
    code = Column(String, nullable=False)
    # make status which is in {active, playing, inactive}
    status = Column(String, nullable=False, default="active")
    host_id = Column(UUID, ForeignKey("users.id"))
    host = relationship("User", backref="rooms")
    created_at = Column(TIMESTAMP, nullable=False, default=current_timestamp())

    #join user in room
    def join(self, user):
        room_user = RoomUser(
            room_id=self.id,
            user_id=user.id,
            is_connected=True,
            entered_at=current_timestamp(),
            sid = None,
        )
        session.add(room_user)
        session.commit()

    #delete room and all roomuser pairs
    def delete(self):
        self.status = "inactive"
        session.query(RoomUser).filter(RoomUser.room_id == self.id).delete()
        session.commit()

    #leave user from room
    def leave(self, user):
        room_user = session.query(RoomUser).filter(RoomUser.room_id == self.id, RoomUser.user_id == user.id).first()
        if room_user:
            #check if room_user is host
            if room_user.user_id == self.host_id:
                #if host leave room, delete room
                self.delete()
            else:
                #if user leave room, delete roomuser pair
                session.delete(room_user)
                session.commit()
        else:
            raise HTTPException(status_code=404, detail="User not found in room")


class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("rooms.id"))
    room = relationship("Room", backref="games")
    started_at = Column(TIMESTAMP, nullable=False, default = current_timestamp())
    time_limit = Column(Integer, nullable=False, default=30)

class GameLog(Base):
    __tablename__ = "game_logs"

    id = Column(Integer, primary_key=True, index=True)
    datetime = Column(TIMESTAMP, nullable=False, default = current_timestamp())
    created_by = Column(UUID, ForeignKey("users.id"))
    creator = relationship("User", backref="game_logs")
    content = Column(String, nullable=False)
    game_id = Column(Integer, ForeignKey("games.id"))
    game = relationship("Game", backref="game_logs")
