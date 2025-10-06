from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional

class UserChatLink(SQLModel, table=True):
    user_id: int = Field(foreign_key="user.id", primary_key=True)
    chat_id: int = Field(foreign_key="chat.id", primary_key=True)

class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    email: str = Field(index=True, unique=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    chats: list["Chat"] = Relationship(back_populates="users", link_model=UserChatLink)
    messages: list["Message"] = Relationship(back_populates="user")

class Chat(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    messages: list["Message"] = Relationship(back_populates="chat")
    users: list["User"] = Relationship(back_populates="chats", link_model=UserChatLink)

class Message(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    sender_id: int = Field(foreign_key="user.id")
    chat_id: int = Field(foreign_key="chat.id")
    file_urls: Optional[str] = None  # JSON со списком URL файлов
    user: "User" = Relationship(back_populates="messages")
    chat: "Chat" = Relationship(back_populates="messages")


class ChatParticipant(SQLModel, table=True):
    chat_id: int = Field(foreign_key="chat.id", primary_key=True)
    user_id: int = Field(foreign_key="user.id", primary_key=True)