from .data_models import SessionLocal
from sqlalchemy.orm import Session

def get_db() -> Session:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()
