from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.db.database import init_db
from app.routers.auth import router as auth_router
from app.routers.chat import router as chat_router
import fastapi
import sqlmodel
import passlib
import jose
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"Starting FastAPI application at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"FastAPI version: {fastapi.__version__}")
    print(f"SQLModel version: {sqlmodel.__version__}")
    print(f"Passlib version: {passlib.__version__}")
    print(f"Python-jose version: {jose.__version__}")
    init_db()
    yield
    print("Shutting down FastAPI application")

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(chat_router)

@app.get("/")
async def root():
    return {"message": "Welcome to WebMessanger API"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)