from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True

class ChatCreate(BaseModel):
    name: str = ""
    recipient_id: int

class MessageCreate(BaseModel):
    content: str
    chat_id: int

class MessageUpdate(BaseModel):
    content: str

class MessageResponse(BaseModel):
    id: int
    content: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    file_urls: Optional[str] = None
    sender_id: int
    chat_id: int

    class Config:
        from_attributes = True