import datetime
from pydantic import BaseModel

# --- Pydantic Schemas ---

# Shared properties for a user
class UserBase(BaseModel):
    phone_number: str
    email: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    channel_preference: str = "sms"

# Properties to receive via API on user creation
class UserCreate(UserBase):
    pass

# Properties to return to the client (includes DB-generated fields)
class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime.datetime

    # This tells Pydantic to read data even if it's not a dict (like a DB object)
    class Config:
        orm_mode = True