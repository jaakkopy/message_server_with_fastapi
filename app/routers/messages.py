from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from ..db import get_db
from ..data_models import Message, User
from .auth import get_current_user

router = APIRouter()


class MessageModel(BaseModel):
    sender: EmailStr
    content: str


@router.get("/messages/unseen", response_model=list[MessageModel])
def get_all_unseen(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    all_unseen = db.query(Message).filter(Message.receiver_id == current_user.id and Message.seen == False)
    return all_unseen