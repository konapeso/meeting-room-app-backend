from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from .database import Base


class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, index=True)
    user_name = Column(String(100), unique=True, index=True)
    user_email = Column(String(100), unique=True, index=True)
    is_executive = Column(Boolean, default=False)
    password_hash = Column(String(128))
    participants = relationship("Participant", back_populates="user")


class Room(Base):
    __tablename__ = "rooms"
    room_id = Column(Integer, primary_key=True, index=True)
    room_name = Column(String(100), unique=True, index=True)
    capacity = Column(Integer)
    room_image = Column(String(255))
    room_type = Column(String(50))


class Booking(Base):
    __tablename__ = "bookings"
    booking_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True
    )
    room_id = Column(
        Integer, ForeignKey("rooms.room_id", ondelete="SET NULL"), nullable=True
    )
    booked_num = Column(Integer)
    start_datetime = Column(DateTime, nullable=False)
    end_datetime = Column(DateTime, nullable=False)
    participants = relationship("Participant", back_populates="booking")


class Participant(Base):
    __tablename__ = "participants"
    participant_id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(
        Integer, ForeignKey("bookings.booking_id", ondelete="CASCADE"), nullable=False
    )
    user_id = Column(
        Integer, ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True
    )
    is_guest = Column(Boolean, default=False)
    guest_email = Column(String(100), nullable=True)
    user = relationship("User", back_populates="participants")
    booking = relationship("Booking", back_populates="participants")
