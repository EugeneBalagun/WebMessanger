from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import FileResponse
from sqlmodel import Session, select
from app.db.database import engine
from app.models.models import Chat, User, Message, UserChatLink
from app.routers.auth import get_current_user
from app.schemas import MessageCreate, ChatCreate, MessageUpdate, MessageResponse
from datetime import datetime
import os
import json
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form

router = APIRouter()

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {'.jpg', '.png', '.pdf', '.doc', '.txt'}


def get_db():
    with Session(engine) as session:
        yield session

@router.post("/chats/", response_model=Chat)
def create_chat(chat: ChatCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    recipient = db.get(User, chat.recipient_id)
    if not recipient:
        raise HTTPException(status_code=404, detail="Recipient not found")
    if recipient.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot create chat with yourself")

    db_chat = Chat(name=f"{current_user.username} and {recipient.username}")
    db.add(db_chat)
    db.commit()
    db.refresh(db_chat)

    db.add(UserChatLink(chat_id=db_chat.id, user_id=current_user.id))
    db.add(UserChatLink(chat_id=db_chat.id, user_id=recipient.id))
    db.commit()
    return db_chat

@router.get("/chats/", response_model=list[Chat])
def get_chats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    stmt = select(Chat).join(UserChatLink).where(UserChatLink.user_id == current_user.id)
    chats = db.exec(stmt).all()
    return chats

@router.get("/chats/{chat_id}", response_model=Chat)
def get_chat(chat_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    stmt = select(Chat).join(UserChatLink).where(
        (Chat.id == chat_id) & (UserChatLink.user_id == current_user.id)
    )
    chat = db.exec(stmt).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    return chat


@router.post("/messages/", response_model=MessageResponse)
async def create_message(
        content: str = Form(...),
        chat_id: int = Form(...),
        files: list[UploadFile] = File(None),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    print(f"=== DEBUG: Creating message ===")
    print(f"Content: {content}")
    print(f"Chat ID: {chat_id} (type: {type(chat_id)})")
    print(f"Current user ID: {current_user.id}")
    print(f"Files: {files}")

    # Проверяем доступ к чату
    stmt = select(Chat).join(UserChatLink).where(
        (Chat.id == chat_id) & (UserChatLink.user_id == current_user.id)
    )
    db_chat = db.exec(stmt).first()
    if not db_chat:
        print(f"=== DEBUG: Chat {chat_id} not found or no access ===")
        raise HTTPException(status_code=404, detail="Chat not found")

    print(f"=== DEBUG: Chat found: {db_chat.name} ===")

    file_urls = []
    if files:
        upload_dir = Path("/app/files")
        upload_dir.mkdir(exist_ok=True)

        MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 МБ, можеш змінити при потребі
        ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".pdf", ".txt"}  # приклад дозволених типів

        for file in files:
            if file.size > MAX_FILE_SIZE:
                raise HTTPException(status_code=400, detail=f"File {file.filename} too large")

            if Path(file.filename).suffix.lower() not in ALLOWED_EXTENSIONS:
                raise HTTPException(status_code=400, detail=f"File type not allowed")

            file_path = upload_dir / file.filename
            with file_path.open("wb") as f:
                content_file = await file.read()
                f.write(content_file)

            file_urls.append(f"/files/{file.filename}")

    db_message = Message(
        content=content,
        chat_id=chat_id,
        sender_id=current_user.id,
        created_at=datetime.utcnow(),
        file_urls=json.dumps(file_urls) if file_urls else None
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

@router.get("/messages/{chat_id}", response_model=list[MessageResponse])
def get_messages(chat_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    stmt = select(Message).where(Message.chat_id == chat_id).order_by(Message.created_at)
    messages = db.exec(stmt).all()
    return messages

@router.put("/messages/{message_id}", response_model=MessageResponse)
def update_message(
    message_id: int,
    message_update: MessageUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    message = db.get(Message, message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    if message.sender_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    message.content = message_update.content
    message.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(message)
    return message

@router.delete("/messages/{message_id}")
def delete_message(message_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    message = db.get(Message, message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    if message.sender_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    db.delete(message)
    db.commit()
    return {"message": "Deleted"}

@router.get("/files/{filename}")
async def get_file(filename: str):
    file_path = Path("/app/files") / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path)