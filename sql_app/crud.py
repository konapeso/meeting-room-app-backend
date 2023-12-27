from sqlalchemy.orm import Session
from . import models, schemas
from fastapi import HTTPException
import bcrypt


# ユーザー一覧を取得
def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


# 会議室一覧を取得
def get_rooms(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Room).offset(skip).limit(limit).all()


# 予約一覧を取得
def get_bookings(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Booking).offset(skip).limit(limit).all()


# パスワードをハッシュ化
def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())


# ユーザー登録
def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = hash_password(user.password)
    db_user = models.User(
        user_name=user.user_name,
        user_email=user.user_email,
        is_executive=user.is_executive,
        password_hash=hashed_password,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# ユーザー認証
def authenticate_user(db: Session, user_id: int, password: str):
    db_user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if db_user and bcrypt.checkpw(password.encode(), db_user.password_hash.encode()):
        return db_user
    return None


# ユーザーを取得
def get_user_by_id(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.user_id == user_id).first()


# 会議室登録
def create_room(db: Session, room: schemas.RoomCreate):
    db_room = models.Room(
        room_name=room.room_name,
        capacity=room.capacity,
        room_image=room.room_image,
        room_type=room.room_type,
    )
    db.add(db_room)
    db.commit()
    db.refresh(db_room)
    return db_room


# 会議室を取得
def get_room_by_id(db: Session, room_id: int):
    return db.query(models.Room).filter(models.Room.room_id == room_id).first()


# 予約登録
def create_booking(db: Session, booking: schemas.BookingCreate):
    db_booked = (
        db.query(models.Booking)
        .filter(models.Booking.room_id == booking.room_id)
        .filter(models.Booking.end_datetime > booking.start_datetime)
        .filter(models.Booking.start_datetime < booking.end_datetime)
        .all()
    )

    # 重複するデータがなければ
    if len(db_booked) == 0:
        db_booking = models.Booking(
            user_id=booking.user_id,
            room_id=booking.room_id,
            booked_num=booking.booked_num,
            start_datetime=booking.start_datetime,
            end_datetime=booking.end_datetime,
        )
        db.add(db_booking)
        db.commit()
        db.refresh(db_booking)

        # 予約に参加者を追加
        for participant in booking.participants:
            db_participant = models.Participant(
                booking_id=db_booking.booking_id,
                user_id=participant.user_id if participant.user_id else None,
                is_guest=participant.is_guest,
                guest_email=participant.guest_email if participant.is_guest else None,
            )
            db.add(db_participant)

        db.commit()

        return db_booking
    else:
        raise HTTPException(status_code=404, detail="Already booked")


# 参加者を予約に追加する関数
def add_participant_to_booking(
    db: Session, booking_id: int, participant: schemas.ParticipantCreate
):
    db_participant = models.Participant(
        **participant.model_dump(), booking_id=booking_id
    )
    db.add(db_participant)
    db.commit()
    db.refresh(db_participant)
    return db_participant


# 特定の予約に関連する参加者リストを取得する関数
def get_participants_for_booking(db: Session, booking_id: int):
    return (
        db.query(models.Participant)
        .filter(models.Participant.booking_id == booking_id)
        .all()
    )


# 特定の予約を取得する関数
def get_booking_by_id(db: Session, booking_id: int):
    return (
        db.query(models.Booking).filter(models.Booking.booking_id == booking_id).first()
    )


# 予約をキャンセルする関数
def cancel_booking(db: Session, booking_id: int):
    # 予約に関連付けられた参加者を削除
    db.query(models.Participant).filter(
        models.Participant.booking_id == booking_id
    ).delete()

    # 予約を削除
    db_booking = get_booking_by_id(db, booking_id=booking_id)
    if db_booking:
        db.delete(db_booking)
        db.commit()
