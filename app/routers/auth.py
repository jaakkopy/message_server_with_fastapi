from pydantic import BaseModel, EmailStr
from fastapi import APIRouter, HTTPException
from ..data_models import User, SessionLocal
import bcrypt
from sqlalchemy.orm import Session
import jwt
from fastapi.security import OAuth2PasswordBearer

router = APIRouter()

class UserModel(BaseModel):
    email: EmailStr
    password: str

class SuccessfulLoginModel(BaseModel):
    email: EmailStr


def hash_password(password: str) -> tuple[bytes]:
    salt = bcrypt.gensalt(rounds=12)
    password = bytes(password, encoding="utf-8")
    hashed = bcrypt.hashpw(password, salt)
    return (hashed, salt)


def verify_password(given: str, stored_salt: bytes) -> bool:
    hashed_given = bcrypt.hashpw(given, stored_salt)
    return bcrypt.checkpw(given, hashed_given)


def authenticate_user(db: Session, user_data: UserModel) -> bool:
    user_with_email: list[User] = db.query(User).filter(User.email == user_data.email).all()
    if not user_with_email:
        return False 
    user_with_email = user_with_email[0]
    if not verify_password(user_data.password, user_with_email.salt):
        return False 
    return True


@router.post("/users/register", response_model=SuccessfulLoginModel)
def register_user(signup_data: UserModel):
    db: Session = SessionLocal()
    existing_users_with_email = db.query(User).filter(User.email == signup_data.email).all()
    if existing_users_with_email:
        raise HTTPException(403, "Email already registered") 
    hashed, salt = hash_password(signup_data.password)
    new_user = User(email=signup_data.email, password_hash=hashed, salt=salt)
    db.add(new_user)
    db.commit()
    db.close()
    return signup_data

# TODO: implementoi login JWT avulla.
@router.post("/users/login")
def login_user(user_data: UserModel):
    pass