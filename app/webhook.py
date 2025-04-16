from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from db import SessionLocal
from models import Room, Message
import uuid

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/message")
async def receive_message(req: Request, db: Session = Depends(get_db)):
    payload = await req.json()

    room_id = payload["room_id"]
    sender = payload["sender_type"]  # "agent", "customer", etc.
    message = payload["message"]["text"]
    timestamp = payload["timestamp"]

    # Upsert Room
    room = db.query(Room).filter_by(id=room_id).first()
    if not room:
        room = Room(id=room_id, channel=payload.get("channel"), phone=payload.get("phone_number"))
        db.add(room)

    # Save message
    msg = Message(
        id=str(uuid.uuid4()),
        room_id=room_id,
        sender=sender,
        content=message,
        timestamp=timestamp,
    )
    db.add(msg)
    db.commit()

    return {"status": "ok"}
