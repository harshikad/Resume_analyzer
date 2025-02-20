from sqlalchemy import create_engine, Column, Integer, String, Text, ARRAY, TIMESTAMP
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime

DATABASE_URL = "postgresql://username:root@localhost/resume_Db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
