import logging
from fastapi import FastAPI
from .setting import User, session, UserCreate  # UserCreate をインポート


# ロギングの設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()


@app.get("/")
async def read_root():
    logger.info("Root endpoint called")
    return {"Hello": "World"}


@app.get("/users/")
def read_users():
    users = session.query(User).all()
    users_data = [
        {
            "id": user.id,
            "name": user.name,
            "fullname": user.fullname,
            "nickname": user.nickname,
        }
        for user in users
    ]
    return {"users": users_data}


@app.post("/users/")
def create_user(user_create: UserCreate):
    new_user = User(
        name=user_create.name,
        fullname=user_create.fullname,
        nickname=user_create.nickname,
    )
    session.add(new_user)
    session.commit()
    return {"message": "User created successfully", "user": user_create}


@app.put("/users/{user_id}")
def update_user(user_id: int, user_update: UserCreate):
    user_to_update = session.query(User).filter(User.id == user_id).first()
    if not user_to_update:
        return {"error": "User not found"}

    user_to_update.name = user_update.name
    user_to_update.fullname = user_update.fullname
    user_to_update.nickname = user_update.nickname
    session.commit()

    return {"message": "User updated successfully", "user": user_update}


@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    user_to_delete = session.query(User).filter(User.id == user_id).first()
    if not user_to_delete:
        return {"error": "User not found"}

    session.delete(user_to_delete)
    session.commit()

    return {"message": "User deleted successfully"}
