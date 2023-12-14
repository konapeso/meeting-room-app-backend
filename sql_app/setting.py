from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base
from pydantic import BaseModel

username = "admin"
password = "zme0aju_hpe1ebm*BWY"
host = "eve-backend-db.cwoji7dwklcq.ap-southeast-2.rds.amazonaws.com"
database = "eve-backend-db"
# データベースエンジンの設定
engine = create_engine(
    f"mysql+pymysql://{username}:{password}@{host}/{database}", echo=True
)

# ベースクラスの作成
Base = declarative_base()


# ユーザーモデルの定義 (SQLAlchemy)
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    fullname = Column(String(255))
    nickname = Column(String(255))


# Pydanticモデルの定義
class UserCreate(BaseModel):
    name: str
    fullname: str
    nickname: str


class UserRead(BaseModel):
    id: int
    name: str
    fullname: str
    nickname: str

    class Config:
        orm_mode = True


# セッションの作成
Session = sessionmaker(bind=engine)
session = Session()

# テーブルの作成
Base.metadata.create_all(engine)

# # CRUD操作
# # Create（作成）
# new_user = User(name="newuser", fullname="New User", nickname="newbie")
# session.add(new_user)
# session.commit()

# # Read（読み込み）
# users = session.query(User).all()
# for user in users:
#     print(user.name, user.fullname, user.nickname)

# # Update（更新）
# user_to_update = session.query(User).filter(User.name == "newuser").first()
# if user_to_update:
#     user_to_update.fullname = "Updated User"
#     session.commit()

# # Delete（削除）
# user_to_delete = session.query(User).filter(User.name == "newuser").first()
# if user_to_delete:
#     session.delete(user_to_delete)
#     session.commit()
