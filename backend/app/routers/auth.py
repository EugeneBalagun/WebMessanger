from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlmodel import Session, select
from app.db.database import engine
from app.models.models import User
from app.schemas import UserCreate, UserResponse
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "c54b87bf2357325b1592791dea87ffc0d5eb94c042959df276e9378f1d46f68b"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    print(f"Creating token with data: {to_encode}")
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    print(f"Token created: {token}")
    return token

def get_db():
    with Session(engine) as session:
        yield session

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Could not validate credentials")
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    stmt = select(User).where(User.username == username)
    user = db.exec(stmt).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    stmt = select(User).where(User.email == user.email)
    db_user = db.exec(stmt).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    stmt = select(User).where(User.username == user.username)
    db_user = db.exec(stmt).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already taken")

    hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    print(f"Username: {form_data.username}")
    stmt = select(User).where(User.username == form_data.username)
    db_user = db.exec(stmt).first()
    print(f"User found: {db_user}")
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username",
            headers={"WWW-Authenticate": "Bearer"}
        )
    print(f"Verifying password for {form_data.password}")
    if not verify_password(form_data.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    print("Creating access token")
    access_token = create_access_token(data={"sub": db_user.username})
    print(f"Token created: {access_token}")
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

# ... (твой код без изменений)
@router.get("/users/", response_model=list[UserResponse])
def get_users(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    stmt = select(User).where(User.id != current_user.id)  # Без себя
    users = db.exec(stmt).all()
    return users


@router.post("/logout")
def logout(current_user: User = Depends(get_current_user)):
    return {"message": "Successfully logged out"}