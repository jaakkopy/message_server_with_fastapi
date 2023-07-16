from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from ..db import get_db
from ..data_models import Message, User
from .auth import get_current_user

router = APIRouter()


class MessageInDB(BaseModel):
    sender: EmailStr
    content: str


class NewMessage(BaseModel):
    receiver: EmailStr
    content: str


def format_messages(db: Session, all_messages: list[Message]) -> list[MessageInDB]:
    formatted_messages = []
    for m in all_messages:
        sender_email = db.query(User).filter(
            User.id == m.sender_id).first().email
        formatted_messages.append(MessageInDB(
            sender=sender_email, content=m.content))
    return formatted_messages


'''
Get all messages, which are marked as seen==False. Set seen==True for each of these and return the messages.
'''


@router.get("/messages/unseen", response_model=list[MessageInDB])
def get_all_unseen(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    all_unseen = db.query(Message).filter(
        Message.receiver_id == current_user.id).filter(Message.seen == False).all()
    for message in all_unseen:
        message.seen = True
    db.commit()
    return format_messages(db, all_unseen)


'''
Get all messages for the current user.
'''


@router.get("/messages/all", response_model=list[MessageInDB])
def get_all_unseen(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    all_messages = db.query(Message).filter(
        Message.receiver_id == current_user.id).all()
    return format_messages(db, all_messages)


'''
Send a new message to another user.
'''


@router.post("/messages/send", status_code=status.HTTP_201_CREATED, response_model=NewMessage)
def get_all_unseen(new_message: NewMessage, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    receiver: User | None = db.query(User).filter(
        User.email == new_message.receiver).first()
    if receiver is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST,
                            "No such email registered")
    sender_id = db.query(User).filter(
        User.email == current_user.email).first().id
    to_add = Message(content=new_message.content,
                     sender_id=sender_id, receiver_id=receiver.id)
    db.add(to_add)
    db.commit()
    return new_message
