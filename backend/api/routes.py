from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List, Dict, Any
import uuid
import os
from datetime import datetime
from loguru import logger

from config import settings
from agents.document_ingestion_agent import DocumentIngestionAgent
from orchestrator.orchestrator_agent import OrchestratorAgent

router = APIRouter(prefix="/api", tags=["automation"])

document_ingestion_agent = DocumentIngestionAgent()
orchestrator = OrchestratorAgent()

# In-memory storage for demo mode
projects_store: Dict[str, Any] = {}
documents_store: Dict[str, List[Any]] = {}


@router.post("/projects")
async def create_project(project_name: str, description: str = ""):
    try:
        project_id = str(uuid.uuid4())
        created_at = datetime.utcnow().isoformat()
        
        project = {
            "project_id": project_id,
            "project_name": project_name,
            "description": description,
            "status": "draft",
            "created_at": created_at,
            "updated_at": created_at,
            "automation_framework": None
        }
        
        projects_store[project_id] = project
        documents_store[project_id] = []
        
        logger.info(f"Project created: {project_id}")
        return {
            "project_id": project_id,
            "project_name": project_name,
            "status": "draft",
            "created_at": created_at
        }
    except Exception as e:
        logger.error(f"Error creating project: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/projects/{project_id}")
async def get_project(project_id: str):
    try:
        if project_id not in projects_store:
            raise HTTPException(status_code=404, detail="Project not found")
        
        project = projects_store[project_id]
        return project
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching project: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/projects/{project_id}/upload")
async def upload_document(
    project_id: str,
    file: UploadFile = File(...),
    document_type: str = "functional_specification"
):
    try:
        if project_id not in projects_store:
            raise HTTPException(status_code=404, detail="Project not found")

        os.makedirs(settings.upload_dir, exist_ok=True)
        file_path = os.path.join(settings.upload_dir, f"{uuid.uuid4()}_{file.filename}")
        
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        document_id = str(uuid.uuid4())
        upload_timestamp = datetime.utcnow().isoformat()
        
        document = {
            "document_id": document_id,
            "project_id": project_id,
            "document_type": document_type,
            "filename": file.filename,
            "file_path": file_path,
            "upload_timestamp": upload_timestamp
        }
        
        documents_store[project_id].append(document)

        logger.info(f"Document uploaded: {document_id}")
        return {
            "document_id": document_id,
            "filename": file.filename,
            "document_type": document_type,
            "upload_timestamp": upload_timestamp
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/projects/{project_id}/generate")
async def generate_automation(project_id: str):
    try:
        if project_id not in projects_store:
            raise HTTPException(status_code=404, detail="Project not found")

        documents = documents_store.get(project_id, [])
        if not documents:
            raise HTTPException(status_code=400, detail="No documents uploaded for this project")

        workflow_id = str(uuid.uuid4())
        
        documents_data = [
            {
                "document_id": doc["document_id"],
                "file_path": doc["file_path"],
                "document_type": doc["document_type"]
            }
            for doc in documents
        ]

        input_data = {
            "project_id": project_id,
            "documents": documents_data
        }

        result = orchestrator.execute_workflow(workflow_id, input_data)

        projects_store[project_id]["status"] = "automation_generated"
        projects_store[project_id]["automation_framework"] = result.get('framework', {}).get('selected_framework', 'python')
        projects_store[project_id]["updated_at"] = datetime.utcnow().isoformat()

        logger.info(f"Automation generated for project: {project_id}")
        return {
            "workflow_id": workflow_id,
            "project_id": project_id,
            "status": "completed",
            "framework": result.get('framework'),
            "total_test_cases": len(result.get('test_cases', [])),
            "total_features": len(result.get('feature_files', [])),
            "total_pages": len(result.get('page_objects', []))
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating automation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/projects/{project_id}/status")
async def get_generation_status(project_id: str):
    try:
        if project_id not in projects_store:
            raise HTTPException(status_code=404, detail="Project not found")

        project = projects_store[project_id]
        documents = documents_store.get(project_id, [])

        return {
            "project_id": project_id,
            "status": project["status"],
            "automation_framework": project.get("automation_framework"),
            "documents_uploaded": len(documents),
            "created_at": project["created_at"],
            "updated_at": project["updated_at"]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}
