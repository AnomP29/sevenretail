from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from db import Base
import datetime

class Room(Base):
    __tablename__ = 'rooms'
    id = Column(String, primary_key=True, index=True)
    channel = Column(String)
    phone = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    messages = relationship("Message", back_populates="room")

class Message(Base):
    __tablename__ = 'messages'
    id = Column(String, primary_key=True, index=True)
    room_id = Column(String, ForeignKey('rooms.id'))
    sender = Column(String)
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    room = relationship("Room", back_populates="messages")
