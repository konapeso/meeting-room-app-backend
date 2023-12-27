from typing import List
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer

from sqlalchemy.orm import Session

from jose import jwt, JWTError
from datetime import datetime, timedelta

from . import crud, models, schemas
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# トークン関連の設定
SECRET_KEY = "your_secret_key"  # 適切なシークレットキーに置き換えてください
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


# 認証エラー用の例外
credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# JWTトークン生成関数
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = (
        datetime.utcnow() + expires_delta
        if expires_delta
        else datetime.utcnow() + timedelta(minutes=15)
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://meeting-room-app-silk.vercel.app"],  # Next.jsサーバーのURL
    allow_credentials=True,
    allow_methods=["*"],  # すべてのHTTPメソッドを許可
    allow_headers=["*"],  # すべてのHTTPヘッダーを許可
)


# トークンをデコードする関数
def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        return {"user_id": user_id}
    except JWTError:
        raise credentials_exception


# Read
@app.get("/users", response_model=List[schemas.User])
async def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


# ユーザー情報を返すエンドポイント
@app.get("/users/me")
async def read_users_me(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = int(payload.get("sub"))
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = crud.get_user_by_id(db, user_id=user_id)
    if user is None:
        raise credentials_exception
    return user


@app.get("/rooms", response_model=List[schemas.Room])
async def read_rooms(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    rooms = crud.get_rooms(db, skip=skip, limit=limit)
    return rooms


@app.get("/rooms/{room_id}", response_model=schemas.Room)
async def read_room(room_id: int, db: Session = Depends(get_db)):
    room = crud.get_room_by_id(db, room_id=room_id)
    if room is None:
        raise HTTPException(status_code=404, detail="Room not found")
    return room


@app.get("/bookings", response_model=List[schemas.Booking])
async def read_bookings(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    bookings = crud.get_bookings(db, skip=skip, limit=limit)
    return bookings


@app.get(
    "/bookings/{booking_id}/participants", response_model=List[schemas.Participant]
)
async def get_participants_for_booking(booking_id: int, db: Session = Depends(get_db)):
    return crud.get_participants_for_booking(db=db, booking_id=booking_id)


# Create
@app.post("/login")
async def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = crud.authenticate_user(db, user.user_id, user.password)
    if db_user:
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(db_user.user_id)}, expires_delta=access_token_expires
        )
        print("Generated token:", access_token)
        return {"access_token": access_token, "token_type": "bearer"}
    raise HTTPException(status_code=400, detail="無効な認証情報")


@app.post("/users", response_model=schemas.User)
async def create_users(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.create_user(db=db, user=user)


@app.post("/rooms", response_model=schemas.Room)
async def create_rooms(room: schemas.RoomCreate, db: Session = Depends(get_db)):
    return crud.create_room(db=db, room=room)


@app.post("/bookings", response_model=schemas.Booking)
async def create_bookings(
    booking: schemas.BookingCreate, db: Session = Depends(get_db)
):
    return crud.create_booking(db=db, booking=booking)


@app.post("/bookings/{booking_id}/participants", response_model=schemas.Participant)
async def add_participant_to_booking(
    booking_id: int,
    participant: schemas.ParticipantCreate,
    db: Session = Depends(get_db),
):
    return crud.add_participant_to_booking(
        db=db, booking_id=booking_id, participant=participant
    )


# Delete
@app.delete("/bookings/{booking_id}")
async def cancel_booking(booking_id: int, db: Session = Depends(get_db)):
    db_booking = crud.get_booking_by_id(db, booking_id=booking_id)
    if not db_booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    crud.cancel_booking(db, booking_id=booking_id)
    return {"detail": "Booking cancelled successfully"}
