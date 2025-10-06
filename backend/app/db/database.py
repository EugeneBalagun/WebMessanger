from sqlmodel import SQLModel, create_engine
from app.models.models import User, Chat, Message, UserChatLink

DATABASE_URL = "postgresql://postgres:kreker55@db:5432/messenger_db"

engine = create_engine(DATABASE_URL, echo=True)

def init_db():
    SQLModel.metadata.create_all(engine)