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


# users = session.query(User).all()
# for user in users:
#     print(user.id, user.name, user.fullname, user.nickname)
