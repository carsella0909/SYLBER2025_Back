from json import loads

from fastapi import HTTPException
from sqlalchemy import create_engine, ForeignKey, UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session, relationship
from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP

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
