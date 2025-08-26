from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

# Import all the necessary components from our other files
from . import crud, schemas
from .db import models
from .db.database import SessionLocal, engine

# This line ensures the tables are created when the app starts
models.Base.metadata.create_all(bind=engine)

# This is the line that was missing
app = FastAPI(title="AiLink.at", version="0.1.0")

# --- Include Routers ---
# This line makes all the endpoints from webhooks.py available
# under the path prefix "/webhooks".
# So, the Telnyx endpoint will be at "/webhooks/telnyx".
# app.include_router(webhooks.router, prefix="/webhooks") # We will uncomment this later


# --- Dependency ---
def get_db():
    """
    This function creates a database session for each request
    and makes sure it's closed afterward.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- API Endpoints ---

@app.post("/users/", response_model=schemas.User)
def create_user_endpoint(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    API endpoint to create a new user.
    """
    db_user = crud.get_user_by_phone_number(db, phone_number=user.phone_number)
    if db_user:
        raise HTTPException(status_code=400, detail="Phone number already registered")
    return crud.create_user(db=db, user=user)


@app.get("/")
def read_root():
    """A simple endpoint to confirm the API is running."""
    return {"status": "ok", "message": "Welcome to AiLink.at"}