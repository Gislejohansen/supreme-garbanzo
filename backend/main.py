from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import uvicorn
import os
from typing import List, Optional
import shutil
from datetime import datetime
import uuid

from .models import database, ProjectCreate, Project
from .services.image_processor import ImageProcessor
from .services.paint_analyzer import PaintAnalyzer

app = FastAPI(
    title="Paint Quality Analysis API",
    description="AI-powered paint quality detection and analysis",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create directories
os.makedirs("uploads", exist_ok=True)
os.makedirs("results", exist_ok=True)

# Static files
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.mount("/results", StaticFiles(directory="results"), name="results")

# Initialize services
image_processor = ImageProcessor()
paint_analyzer = PaintAnalyzer()

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.get("/")
async def root():
    return {"message": "Paint Quality Analysis API"}

@app.post("/api/projects", response_model=Project)
async def create_project(project: ProjectCreate):
    """Create a new paint analysis project"""
    project_id = str(uuid.uuid4())
    project_data = {
        "id": project_id,
        "name": project.name,
        "description": project.description,
        "created_at": datetime.utcnow(),
        "status": "created"
    }
    
    # Save to database (implementation depends on your database setup)
    # For now, we'll return the project data
    return Project(**project_data)

@app.post("/api/projects/{project_id}/upload-before")
async def upload_before_image(project_id: str, file: UploadFile = File(...)):
    """Upload before painting image"""
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Create project directory
    project_dir = f"uploads/{project_id}"
    os.makedirs(project_dir, exist_ok=True)
    
    # Save file
    file_path = f"{project_dir}/before_{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Process image
    processed_image = await image_processor.process_image(file_path)
    
    return {
        "message": "Before image uploaded successfully",
        "file_path": file_path,
        "processed": processed_image
    }

@app.post("/api/projects/{project_id}/upload-after")
async def upload_after_image(project_id: str, file: UploadFile = File(...)):
    """Upload after painting image"""
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    project_dir = f"uploads/{project_id}"
    os.makedirs(project_dir, exist_ok=True)
    
    file_path = f"{project_dir}/after_{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    processed_image = await image_processor.process_image(file_path)
    
    return {
        "message": "After image uploaded successfully",
        "file_path": file_path,
        "processed": processed_image
    }

@app.post("/api/projects/{project_id}/analyze")
async def analyze_paint_quality(project_id: str):
    """Analyze paint quality by comparing before and after images"""
    project_dir = f"uploads/{project_id}"
    
    # Find before and after images
    before_images = [f for f in os.listdir(project_dir) if f.startswith("before_")]
    after_images = [f for f in os.listdir(project_dir) if f.startswith("after_")]
    
    if not before_images or not after_images:
        raise HTTPException(status_code=400, detail="Both before and after images are required")
    
    before_path = f"{project_dir}/{before_images[0]}"
    after_path = f"{project_dir}/{after_images[0]}"
    
    # Perform analysis
    analysis_result = await paint_analyzer.analyze_paint_quality(
        before_path, after_path, project_id
    )
    
    return analysis_result

@app.get("/api/projects/{project_id}/results")
async def get_analysis_results(project_id: str):
    """Get analysis results for a project"""
    results_path = f"results/{project_id}/analysis_result.json"
    
    if not os.path.exists(results_path):
        raise HTTPException(status_code=404, detail="Analysis results not found")
    
    import json
    with open(results_path, 'r') as f:
        results = json.load(f)
    
    return results

@app.get("/api/projects")
async def list_projects():
    """List all projects"""
    projects = []
    if os.path.exists("uploads"):
        for project_id in os.listdir("uploads"):
            if os.path.isdir(f"uploads/{project_id}"):
                projects.append({
                    "id": project_id,
                    "name": f"Project {project_id[:8]}",
                    "created_at": datetime.fromtimestamp(
                        os.path.getctime(f"uploads/{project_id}")
                    ).isoformat()
                })
    
    return {"projects": projects}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)