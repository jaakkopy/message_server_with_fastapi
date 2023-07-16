from dataclasses import dataclass
from sqlalchemy import Column, String, Integer, BLOB, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from dotenv import load_dotenv
from os import getenv

Base = declarative_base()


@dataclass
class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(BLOB)
    salt = Column(BLOB)
    messages = relationship("Message", backref="message")


@dataclass
class Message(Base):
    __tablename__ = "message"
    id = Column(Integer, primary_key=True, autoincrement=True)
    content = Column(String)
    sender_id = Column(Integer, ForeignKey("user.id"))
    receiver_id = Column(Integer, ForeignKey("user.id"))


load_dotenv()
engine = create_engine(getenv("CONNECTION_STR"), echo=True)
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
