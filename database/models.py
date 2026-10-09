from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from database.db import Base
import uuid

class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    event_name = Column(String, nullable=False)
    status = Column(String, default="PENDING") 
    total_recipients = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    

    certificates = relationship("Certificate", back_populates="job")

class Certificate(Base):
    __tablename__ = "certificates"
    
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    job_id = Column(String, ForeignKey("jobs.id"))
    recipient_name = Column(String, nullable=False)
    recipient_email = Column(String, nullable=False)
    status = Column(String, default="PENDING") # PENDING, SUCCESS, FAILED
    file_url = Column(String, nullable=True) # S3 or local path
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    

    job = relationship("Job", back_populates="certificates")
