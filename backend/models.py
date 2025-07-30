from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy import create_engine, Column, String, DateTime, Text, Float, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import databases
import os

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./paint_analysis.db")
database = databases.Database(DATABASE_URL)
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Pydantic models for API
class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None

class Project(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    created_at: datetime
    status: str
    
    class Config:
        from_attributes = True

class ImageInfo(BaseModel):
    filename: str
    file_path: str
    upload_time: datetime
    image_type: str  # "before" or "after"
    file_size: int
    dimensions: Dict[str, int]  # {"width": 1920, "height": 1080}

class AnalysisRegion(BaseModel):
    x: int
    y: int
    width: int
    height: int
    severity: float  # 0-1 scale
    issue_type: str  # "uneven_coverage", "color_inconsistency", "texture_variation"
    confidence: float  # 0-1 scale

class AnalysisResult(BaseModel):
    project_id: str
    overall_score: float  # 0-100 scale
    issues_detected: int
    regions: List[AnalysisRegion]
    analysis_time: datetime
    processing_duration: float  # seconds
    recommendations: List[str]
    color_analysis: Dict[str, Any]
    coverage_analysis: Dict[str, Any]

class ProjectAnalysis(BaseModel):
    project: Project
    before_image: Optional[ImageInfo] = None
    after_image: Optional[ImageInfo] = None
    analysis_result: Optional[AnalysisResult] = None

# SQLAlchemy models
class ProjectTable(Base):
    __tablename__ = "projects"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime)
    status = Column(String)

class ImageTable(Base):
    __tablename__ = "images"
    
    id = Column(String, primary_key=True, index=True)
    project_id = Column(String, index=True)
    filename = Column(String)
    file_path = Column(String)
    upload_time = Column(DateTime)
    image_type = Column(String)
    file_size = Column(Integer)
    width = Column(Integer)
    height = Column(Integer)

class AnalysisTable(Base):
    __tablename__ = "analyses"
    
    id = Column(String, primary_key=True, index=True)
    project_id = Column(String, index=True)
    overall_score = Column(Float)
    issues_detected = Column(Integer)
    analysis_time = Column(DateTime)
    processing_duration = Column(Float)
    result_data = Column(Text)  # JSON string of full analysis result

# Create tables
Base.metadata.create_all(bind=engine)