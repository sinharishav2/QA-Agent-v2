from sqlalchemy.orm import Session
from models.database import ProjectDB, DocumentDB, RequirementDB, TestCaseDB
from models.schemas import Project
from loguru import logger
import uuid
from datetime import datetime


class ProjectService:
    @staticmethod
    def create_project(db: Session, project_name: str, description: str = "") -> ProjectDB:
        project = ProjectDB(
            project_id=str(uuid.uuid4()),
            project_name=project_name,
            description=description,
            status="draft"
        )
        db.add(project)
        db.commit()
        db.refresh(project)
        logger.info(f"Project created: {project.project_id}")
        return project

    @staticmethod
    def get_project(db: Session, project_id: str) -> ProjectDB:
        return db.query(ProjectDB).filter(ProjectDB.project_id == project_id).first()

    @staticmethod
    def list_projects(db: Session, skip: int = 0, limit: int = 100):
        return db.query(ProjectDB).offset(skip).limit(limit).all()

    @staticmethod
    def update_project_status(db: Session, project_id: str, status: str) -> ProjectDB:
        project = ProjectService.get_project(db, project_id)
        if project:
            project.status = status
            project.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(project)
            logger.info(f"Project {project_id} status updated to {status}")
        return project

    @staticmethod
    def delete_project(db: Session, project_id: str) -> bool:
        project = ProjectService.get_project(db, project_id)
        if project:
            db.delete(project)
            db.commit()
            logger.info(f"Project deleted: {project_id}")
            return True
        return False

    @staticmethod
    def get_project_statistics(db: Session, project_id: str) -> dict:
        project = ProjectService.get_project(db, project_id)
        if not project:
            return {}

        documents = db.query(DocumentDB).filter(DocumentDB.project_id == project_id).count()
        requirements = db.query(RequirementDB).filter(RequirementDB.project_id == project_id).count()
        test_cases = db.query(TestCaseDB).filter(TestCaseDB.project_id == project_id).count()

        return {
            "project_id": project_id,
            "project_name": project.project_name,
            "status": project.status,
            "documents_count": documents,
            "requirements_count": requirements,
            "test_cases_count": test_cases,
            "created_at": project.created_at,
            "updated_at": project.updated_at
        }
