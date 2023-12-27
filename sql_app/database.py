from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base
from pydantic import BaseModel

# username = "admin"
# password = "zme0aju_hpe1ebm*BWY"
# host = "eve-backend-db.cwoji7dwklcq.ap-southeast-2.rds.amazonaws.com"
# database = "eve-backend-db"
# データベースエンジンの設定
# engine = create_engine(
#     f"mysql+pymysql://{username}:{password}@{host}/{database}", echo=True
# )
engine = create_engine(
    "mysql+pymysql://user:userpassword@localhost:3306/demo", echo=True
)

# ベースクラスの作成
Base = declarative_base()

# セッションの作成
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
