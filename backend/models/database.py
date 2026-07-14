from sqlalchemy import create_engine, Column, String, DateTime, JSON, Integer, Float, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from config import settings

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class ProjectDB(Base):
    __tablename__ = "projects"

    project_id = Column(String, primary_key=True, index=True)
    project_name = Column(String, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = Column(String, default="draft")
    automation_framework = Column(String, nullable=True)

    documents = relationship("DocumentDB", back_populates="project")
    requirements = relationship("RequirementDB", back_populates="project")
    test_cases = relationship("TestCaseDB", back_populates="project")
    automation_models = relationship("AutomationModelDB", back_populates="project")
    execution_results = relationship("ExecutionResultDB", back_populates="project")


class DocumentDB(Base):
    __tablename__ = "uploaded_documents"

    document_id = Column(String, primary_key=True, index=True)
    project_id = Column(String, ForeignKey("projects.project_id"))
    document_type = Column(String)
    filename = Column(String)
    file_path = Column(String)
    upload_timestamp = Column(DateTime, default=datetime.utcnow)
    parsed_content = Column(JSON, nullable=True)

    project = relationship("ProjectDB", back_populates="documents")


class RequirementDB(Base):
    __tablename__ = "parsed_requirements"

    requirement_id = Column(String, primary_key=True, index=True)
    project_id = Column(String, ForeignKey("projects.project_id"))
    feature = Column(String)
    business_rules = Column(JSON, default=list)
    workflows = Column(JSON, default=list)
    validations = Column(JSON, default=list)
    preconditions = Column(JSON, default=list)
    dependencies = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("ProjectDB", back_populates="requirements")


class TestCaseDB(Base):
    __tablename__ = "manual_test_cases"

    test_id = Column(String, primary_key=True, index=True)
    project_id = Column(String, ForeignKey("projects.project_id"))
    scenario = Column(String)
    preconditions = Column(JSON, default=list)
    steps = Column(JSON, default=list)
    expected_results = Column(JSON, default=list)
    test_data = Column(JSON, default=dict)
    priority = Column(String, default="medium")
    module = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("ProjectDB", back_populates="test_cases")


class AutomationModelDB(Base):
    __tablename__ = "automation_models"

    model_id = Column(String, primary_key=True, index=True)
    project_id = Column(String, ForeignKey("projects.project_id"))
    requirements = Column(JSON, default=list)
    test_cases = Column(JSON, default=list)
    locators = Column(JSON, default=dict)
    pages = Column(JSON, default=list)
    assertions = Column(JSON, default=list)
    business_rules = Column(JSON, default=list)
    generated_scripts = Column(JSON, default=list)
    model_metadata = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    project = relationship("ProjectDB", back_populates="automation_models")


class GeneratedScriptDB(Base):
    __tablename__ = "generated_scripts"

    script_id = Column(String, primary_key=True, index=True)
    project_id = Column(String, ForeignKey("projects.project_id"))
    script_type = Column(String)
    content = Column(Text)
    framework = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)


class ExecutionResultDB(Base):
    __tablename__ = "execution_results"

    result_id = Column(String, primary_key=True, index=True)
    project_id = Column(String, ForeignKey("projects.project_id"))
    test_id = Column(String)
    status = Column(String)
    execution_time = Column(Float)
    screenshots = Column(JSON, default=list)
    logs = Column(JSON, default=list)
    console_errors = Column(JSON, default=list)
    network_logs = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("ProjectDB", back_populates="execution_results")


class AgentLogDB(Base):
    __tablename__ = "agent_logs"

    log_id = Column(String, primary_key=True, index=True)
    project_id = Column(String, ForeignKey("projects.project_id"))
    agent_name = Column(String)
    input_data = Column(JSON)
    output_data = Column(JSON)
    status = Column(String)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class PromptVersionDB(Base):
    __tablename__ = "prompt_versions"

    prompt_id = Column(String, primary_key=True, index=True)
    agent_name = Column(String)
    prompt_content = Column(Text)
    version = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)


class BuildHistoryDB(Base):
    __tablename__ = "build_history"

    build_id = Column(String, primary_key=True, index=True)
    project_id = Column(String, ForeignKey("projects.project_id"))
    framework = Column(String)
    status = Column(String)
    build_output = Column(Text, nullable=True)
    error_log = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
