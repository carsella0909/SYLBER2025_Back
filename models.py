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

class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    max_users = Column(Integer, nullable=False, default=8)
    code = Column(String, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    host_id = Column(UUID, ForeignKey("users.id"))
    host = relationship("User", backref="rooms")
    created_at = Column(TIMESTAMP, nullable=False, default = current_timestamp())

class RoomUser(Base):
    __tablename__ = "room_users"

    room_id = Column(Integer, ForeignKey("rooms.id"), primary_key=True)
    room = relationship("Room", backref="room_users")
    user_id = Column(UUID, ForeignKey("users.id"), primary_key=True)
    user = relationship("User", backref="room_users")
    is_connected = Column(Boolean, nullable=False, default=True)
    entered_at = Column(TIMESTAMP, nullable=False, default = current_timestamp())
    # use (room_id, user_id) as primary key
    __table_args__ = (
        PrimaryKeyConstraint('room_id', 'user_id'),
    )

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
