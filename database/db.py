from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os
load_dotenv()

SQLALCHEMY_DATABASE_URL = "sqlite:///./certificates.db"

if os.getenv("POSTGRESQL_URL"):
    engine = create_engine(
        os.getenv("POSTGRESQL_URL"),
        connect_args={"prepare_threshold": None}
    )
else:
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
