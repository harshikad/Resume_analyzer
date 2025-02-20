from sqlalchemy import Column, Integer, String, Text, ARRAY, TIMESTAMP
from .database import Base
from datetime import datetime
from backend.database import Base


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String, index=True)
    name = Column(String)
    email = Column(String)
    phone = Column(String)
    core_skills = Column(ARRAY(String))
    soft_skills = Column(ARRAY(String))
    experience = Column(Text)
    education = Column(Text)
    projects = Column(Text)
    certifications = Column(Text)
    resume_rating = Column(Integer)
    improvement_areas = Column(Text)
    upskill_suggestions = Column(Text)
    upload_date = Column(TIMESTAMP, default=datetime.utcnow)
