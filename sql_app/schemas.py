import datetime
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional


# Login Schema
class UserLogin(BaseModel):
    user_id: int
    password: str


# UserBase Schema
class UserBase(BaseModel):
    user_name: str = Field(max_length=100)
    user_email: EmailStr
    is_executive: bool


# UserCreate Schema
class UserCreate(UserBase):
    password: str = Field(min_length=8)


# User Schema
class User(UserBase):
    user_id: int

    class Config:
        orm_mode = True


# RoomBase Schema
class RoomBase(BaseModel):
    room_name: str = Field(max_length=100)
    capacity: int
    room_image: Optional[str] = None
    room_type: str


# RoomCreate Schema
class RoomCreate(RoomBase):
    pass


# Room Schema
class Room(RoomBase):
    room_id: int

    class Config:
        orm_mode = True


# ParticipantBase Schema
class ParticipantBase(BaseModel):
    user_id: Optional[int] = None  # Nullable for guests
    is_guest: bool = False
    guest_email: Optional[EmailStr] = None


# ParticipantCreate Schema
class ParticipantCreate(ParticipantBase):
    pass


# Participant Schema
class Participant(ParticipantBase):
    participant_id: int

    class Config:
        orm_mode = True


# BookingBase Schema
class BookingBase(BaseModel):
    user_id: int
    room_id: int
    booked_num: int
    start_datetime: datetime.datetime
    end_datetime: datetime.datetime


# BookingCreate Schema
class BookingCreate(BookingBase):
    participants: List[ParticipantCreate] = []


# Booking Schema
class Booking(BookingBase):
    booking_id: int

    class Config:
        orm_mode = True
