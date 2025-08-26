import os
from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import telnyx

# Import our CRUD functions, schemas, and the get_db dependency
from .. import crud, schemas
from ..db.database import SessionLocal

# --- Configuration ---
load_dotenv()
TELNYX_API_KEY = os.getenv("TELNYX_API_KEY")

# CRITICAL CHECK: Make sure the API key is loaded
if not TELNYX_API_KEY:
    raise RuntimeError("TELNYX_API_KEY not found in .env file. Please check your configuration.")

telnyx.api_key = TELNYX_API_KEY

router = APIRouter()

# --- Dependency to get DB session ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Webhook Endpoint ---
@router.post("/telnyx")
async def webhook_telnyx(request: Request, db: Session = Depends(get_db)):
    """
    Handles incoming SMS from Telnyx and creates a user if they don't exist.
    """
    try:
        payload = await request.body()
        event = telnyx.Event.construct_from(payload.decode('utf-8'), telnyx.api_key)

        if event.data.event_type == "message.received":
            message_body = event.data.payload.get('text', '').strip()
            from_number = event.data.payload.get('from', {}).get('phone_number')

            if not from_number:
                print("❗️ ERROR: Received message without a 'from' number.")
                return {"status": "error", "detail": "Missing from_number"}

            print("--- 📩 New Telnyx Message ---")
            print(f"From: {from_number}")
            print(f"Body: '{message_body}'")
            
            db_user = crud.get_user_by_phone_number(db, phone_number=from_number)
            
            if db_user:
                print(f"✅ User {from_number} already exists.")
            else:
                print(f"✨ User {from_number} not found. Creating new user...")
                new_user_data = schemas.UserCreate(phone_number=from_number)
                crud.create_user(db=db, user=new_user_data)
                print(f"🎉 Successfully created new user for {from_number}.")

            print("------------------------------")

    except Exception as e:
        # This will now print a detailed error to your uvicorn terminal
        print(f"❗️❗️❗️ CRITICAL WEBHOOK ERROR: {e}")
        # It's better to still return a 200 so Telnyx doesn't retry constantly
        return {"status": "error", "detail": str(e)}
    
    return {"status": "ok"}