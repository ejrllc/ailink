from sqlalchemy.orm import Session
from .db import models  # Correctly import models from the db sub-package
from . import schemas  # Correctly import schemas from the current package

def get_user_by_phone_number(db: Session, phone_number: str):
    """
    Retrieves a user from the database by their phone number.
    """
    return db.query(models.User).filter(models.User.phone_number == phone_number).first()

def create_user(db: Session, user: schemas.UserCreate):
    """
    Creates a new user in the database based on the provided schema.
    """
    db_user = models.User(
        phone_number=user.phone_number,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        channel_preference=user.channel_preference
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user