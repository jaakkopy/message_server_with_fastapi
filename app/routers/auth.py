from pydantic import BaseModel, EmailStr
from fastapi import APIRouter, HTTPException, Depends, status
from ..data_models import User, SessionLocal
import bcrypt
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
from datetime import datetime, timedelta
from dotenv import load_dotenv
from os import getenv


'''
NOTE: about 50% of the code here is copied from the documentation: https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/
'''

load_dotenv()
router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class UserData(BaseModel):
    email: EmailStr
    password: str


class SuccessfulRegister(BaseModel):
    email: EmailStr


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


def hash_password(password: str) -> tuple[bytes]:
    salt = bcrypt.gensalt(rounds=12)
    password = bytes(password, encoding="utf-8")
    hashed = bcrypt.hashpw(password, salt)
    return (hashed, salt)


def verify_password(given: str, stored_salt: bytes) -> bool:
    given = bytes(given, encoding="utf-8")
    hashed_given = bcrypt.hashpw(given, stored_salt)
    return bcrypt.checkpw(given, hashed_given)


def authenticate_user(db: Session, email: EmailStr, password: str) -> bool:
    user_with_email: list[User] = db.query(
        User).filter(User.email == email).first()
    if not user_with_email:
        return False
    if not verify_password(password, user_with_email.salt):
        return False
    return True


def get_user_by_email(db: Session, email: EmailStr) -> User:
    user_with_email: list[User] = db.query(
        User).filter(User.email == email).first()
    return user_with_email


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, getenv(
        "SECRET_KEY"), algorithm=getenv("ALGORITHM"))
    return encoded_jwt


def verify_jwt(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, getenv("SECRET_KEY"),
                             algorithms=[getenv("ALGORITHM")])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    db = SessionLocal()
    user = get_user_by_email(db, username=token_data.username)
    db.close()
    if user is None:
        raise credentials_exception
    return user


@router.post("/users/register", response_model=SuccessfulRegister)
def register_user(signup_data: UserData):
    db: Session = SessionLocal()
    existing_users_with_email = db.query(User).filter(
        User.email == signup_data.email).all()
    if existing_users_with_email:
        raise HTTPException(status.HTTP_403_FORBIDDEN,
                            "Email already registered")
    (hashed, salt) = hash_password(signup_data.password)
    new_user = User(email=signup_data.email, password_hash=hashed, salt=salt)
    db.add(new_user)
    db.commit()
    db.close()
    return signup_data


@router.post("/users/login", response_model=Token)
def login_user(user_data: UserData):
    db = SessionLocal()
    auth_result = authenticate_user(db, user_data.email, user_data.password)
    db.close()
    if not auth_result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(
        minutes=int(getenv("ACCESS_TOKEN_EXPIRE_MINUTES")))
    access_token = create_access_token(
        data={"sub": user_data.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
