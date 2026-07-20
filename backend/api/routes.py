from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import uuid
import os
import json
import zipfile
import io
from datetime import datetime
from loguru import logger
from fastapi.responses import StreamingResponse

from config import settings
from agents.document_ingestion_agent import DocumentIngestionAgent

router = APIRouter(prefix="/api", tags=["automation"])

document_ingestion_agent = DocumentIngestionAgent()
orchestrator = None

def set_orchestrator(orch):
    global orchestrator
    orchestrator = orch

# In-memory storage for demo mode
projects_store: Dict[str, Any] = {}
documents_store: Dict[str, List[Any]] = {}

# Storage file paths
PROJECTS_FILE = "projects_data.json"
DOCUMENTS_FILE = "documents_data.json"

def load_storage():
    """Load projects and documents from disk"""
    global projects_store, documents_store
    try:
        if os.path.exists(PROJECTS_FILE):
            with open(PROJECTS_FILE, 'r') as f:
                projects_store = json.load(f)
                logger.info(f"Loaded {len(projects_store)} projects from disk")
        if os.path.exists(DOCUMENTS_FILE):
            with open(DOCUMENTS_FILE, 'r') as f:
                documents_store = json.load(f)
                logger.info(f"Loaded documents from disk")
    except Exception as e:
        logger.warning(f"Could not load storage from disk: {str(e)}")

def save_storage():
    """Save projects and documents to disk"""
    try:
        with open(PROJECTS_FILE, 'w') as f:
            json.dump(projects_store, f, indent=2)
        with open(DOCUMENTS_FILE, 'w') as f:
            json.dump(documents_store, f, indent=2)
        logger.debug("Storage saved to disk")
    except Exception as e:
        logger.warning(f"Could not save storage to disk: {str(e)}")


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
        save_storage()
        
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


@router.delete("/projects/{project_id}")
async def delete_project(project_id: str):
    try:
        if project_id not in projects_store:
            raise HTTPException(status_code=404, detail="Project not found")
        del projects_store[project_id]
        if project_id in documents_store:
            del documents_store[project_id]
        save_storage()
        logger.info(f"Project deleted: {project_id}")
        return {"message": "Project deleted successfully", "project_id": project_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting project: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/projects/{project_id}/upload")
async def upload_document(
    project_id: str,
    file: UploadFile = File(...),
    document_type: str = Form(...)
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
        save_storage()

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
        logger.info(f"Generate request for project: {project_id}")
        
        if project_id not in projects_store:
            logger.error(f"Project not found: {project_id}")
            raise HTTPException(status_code=404, detail="Project not found")

        documents = documents_store.get(project_id, [])
        logger.info(f"Found {len(documents)} documents for project {project_id}")
        
        if not documents:
            logger.error(f"No documents uploaded for project: {project_id}")
            raise HTTPException(status_code=400, detail="No documents uploaded for this project")

        # Validate that all 3 required file types are present
        required_types = {"functional_specification", "test_cases", "expected_output"}
        uploaded_types = {doc["document_type"] for doc in documents}
        
        logger.info(f"Required types: {required_types}")
        logger.info(f"Uploaded types: {uploaded_types}")
        
        missing_types = required_types - uploaded_types
        if missing_types:
            missing_list = ", ".join(missing_types)
            logger.error(f"Missing document types: {missing_list}")
            raise HTTPException(
                status_code=400, 
                detail=f"Missing required documents: {missing_list}. Please upload all 3 files: functional specification, test cases, and expected output."
            )

        workflow_id = str(uuid.uuid4())
        logger.info(f"Starting workflow: {workflow_id}")
        
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

        logger.info(f"Executing workflow with {len(documents_data)} documents")
        result = orchestrator.execute_workflow(workflow_id, input_data)
        logger.info(f"Workflow completed successfully")

        validation_result = result.get('validation_result', {})
        quality_metrics = validation_result.get('validation_score', {})

        projects_store[project_id]["status"] = "automation_generated"
        projects_store[project_id]["automation_framework"] = result.get('framework', {}).get('selected_framework', 'python')
        projects_store[project_id]["updated_at"] = datetime.utcnow().isoformat()
        projects_store[project_id]["generated_artifacts"] = {
            "test_cases": result.get('test_cases', []),
            "feature_files": result.get('feature_files', []),
            "page_objects": result.get('page_objects', []),
            "step_definitions": result.get('step_definitions', []),
            "utilities": result.get('utilities', {}),
            "framework": result.get('framework', {}),
            "quality_metrics": quality_metrics,
            "traceability_map": result.get('traceability_map', {}),
            "requirements": result.get('requirements', []),
        }
        save_storage()

        feature_files = result.get('feature_files', [])
        page_objects = result.get('page_objects', [])
        step_definitions = result.get('step_definitions', [])
        test_cases = result.get('test_cases', [])
        requirements = result.get('requirements', [])
        utilities = result.get('utilities', {})

        logger.info(f"Automation generated for project: {project_id}")
        return {
            "workflow_id": workflow_id,
            "project_id": project_id,
            "status": "completed",
            "framework": result.get('framework'),
            "total_test_cases": len(test_cases),
            "total_features": len(feature_files),
            "total_pages": len(page_objects),
            "total_step_definitions": len(step_definitions),
            "total_utilities": len(utilities) if isinstance(utilities, dict) else 0,
            "total_requirements": len(requirements),
            "total_expected_outputs": sum(
                1 for d in documents_data if d.get("document_type") == "expected_output"
            ),
            "quality_metrics": quality_metrics,
            "validation_summary": quality_metrics.get("summary", ""),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating automation: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/projects/{project_id}/download")
async def download_generated_files(project_id: str):
    try:
        if project_id not in projects_store:
            raise HTTPException(status_code=404, detail="Project not found")

        artifacts = projects_store[project_id].get("generated_artifacts")
        if not artifacts:
            raise HTTPException(status_code=404, detail="No generated files found. Please generate first.")

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Feature files (BDD .feature)
            for i, feature in enumerate(artifacts.get('feature_files', [])):
                content = feature.get('content') or feature.get('feature_content') or json.dumps(feature, indent=2)
                filename = feature.get('filename') or f'feature_{i+1}.feature'
                zip_file.writestr(f"src/test/resources/features/{filename}", content)

            # Page objects
            for i, page in enumerate(artifacts.get('page_objects', [])):
                content = page.get('content') or page.get('class_content') or json.dumps(page, indent=2)
                filename = page.get('filename') or f'Page_{i+1}.java'
                zip_file.writestr(f"src/test/java/pages/{filename}", content)

            # Step definitions
            for i, step in enumerate(artifacts.get('step_definitions', [])):
                content = step.get('content') or step.get('step_content') or json.dumps(step, indent=2)
                filename = step.get('filename') or f'StepDefs_{i+1}.java'
                zip_file.writestr(f"src/test/java/stepdefinitions/{filename}", content)

            # Test cases as JSON
            test_cases = artifacts.get('test_cases', [])
            if test_cases:
                zip_file.writestr("test_cases.json", json.dumps(test_cases, indent=2))

            # Framework utility files (DriverFactory, ConfigReader, Hooks, etc.)
            utilities = artifacts.get('utilities', {})
            if isinstance(utilities, dict):
                for util_name, util_data in utilities.items():
                    if isinstance(util_data, dict) and util_data.get('content'):
                        filename = util_data.get('filename', f'{util_name}.java')
                        zip_file.writestr(f"src/test/java/utils/{filename}", util_data['content'])

            # Quality metrics
            quality_metrics = artifacts.get('quality_metrics', {})

            # Summary JSON
            summary = {
                "project_id": project_id,
                "generated_at": datetime.utcnow().isoformat() + "Z",
                "framework": artifacts.get('framework', {}),
                "total_test_cases": len(test_cases),
                "total_features": len(artifacts.get('feature_files', [])),
                "total_pages": len(artifacts.get('page_objects', [])),
                "total_step_definitions": len(artifacts.get('step_definitions', [])),
                "quality_metrics": quality_metrics,
            }
            zip_file.writestr("summary.json", json.dumps(summary, indent=2))

            # Traceability map
            traceability_map = artifacts.get('traceability_map', {})
            if traceability_map:
                zip_file.writestr("traceability.json", json.dumps(traceability_map, indent=2))

            # README.md
            framework_details = artifacts.get('framework', {})
            fw_name = framework_details.get('selected_framework', 'java')
            quality_score = quality_metrics.get('overall_score', 'N/A')
            readme_content = f"""# QA Automation Project
Generated by QA Agent v2

## Generation Details
- **Generated At**: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC
- **Project ID**: {project_id}
- **Framework**: {fw_name.upper()} / Selenium + Cucumber (BDD)
- **Quality Score**: {quality_score}/100

## Artifact Summary
| Artifact | Count |
|---|---|
| Feature Files (.feature) | {len(artifacts.get('feature_files', []))} |
| Page Object Classes (.java) | {len(artifacts.get('page_objects', []))} |
| Step Definition Classes (.java) | {len(artifacts.get('step_definitions', []))} |
| Test Cases | {len(test_cases)} |

## Project Structure
```
src/
└── test/
    ├── java/
    │   ├── pages/              # Selenium Page Object classes
    │   ├── stepdefinitions/    # Cucumber Step Definition classes
    │   ├── utils/              # DriverFactory, ConfigReader, Hooks
    │   └── runners/            # TestRunner
    └── resources/
        └── features/           # Cucumber .feature files (Gherkin)
```

## Prerequisites
- Java JDK 11+
- Maven 3.6+
- Chrome browser + ChromeDriver on PATH

## Running the Tests
```bash
# Run all tests
mvn clean test

# Run by tag
mvn test -Dcucumber.filter.tags="@smoke"

# Generate reports
# Reports will appear at: target/cucumber-reports/
```

## Quality Metrics
- Overall Score: {quality_score}/100
- Gherkin Quality: {quality_metrics.get('gherkin_quality', 'N/A')}/100
- Java Code Quality: {quality_metrics.get('java_code_quality', 'N/A')}/100
- Step Definition Coverage: {quality_metrics.get('step_definition_coverage', 'N/A')}/100
- Page Object Quality: {quality_metrics.get('page_object_quality', 'N/A')}/100
- Framework Structure: {quality_metrics.get('framework_structure', 'N/A')}/100

{('## Improvement Suggestions' + chr(10) + chr(10).join('- ' + s for s in quality_metrics.get('improvement_suggestions', []))) if quality_metrics.get('improvement_suggestions') else ''}
"""
            zip_file.writestr("README.md", readme_content)

        zip_buffer.seek(0)
        return StreamingResponse(
            zip_buffer,
            media_type="application/zip",
            headers={"Content-Disposition": f"attachment; filename=qa_automation_{project_id[:8]}.zip"}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading files: {str(e)}", exc_info=True)
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


class ChatRequest(BaseModel):
    message: str
    project_id: Optional[str] = None


@router.post("/chat")
async def chat_endpoint(request: ChatRequest):
    from utils.openai_client import openai_client

    system_prompt = """You are an intelligent assistant embedded inside the QA Automation Platform.

Your purpose is to help users understand and use this platform, which automatically generates
production-ready Java Selenium + Cucumber BDD automation test code from uploaded documents.

== PLATFORM OVERVIEW ==
This platform takes user-provided specification documents and uses AI to generate a complete,
runnable Java Selenium + Cucumber test automation framework.

== SUPPORTED INPUT DOCUMENTS (all 3 are required to generate) ==
1. Functional Specification  ->  accepted formats: .txt, .docx, .pdf
   Describes what the application under test does (pages, features, user flows).
2. Test Cases  ->  accepted formats: .txt, .docx, .xlsx, .csv
   Lists test scenarios with steps and expected results.
3. Expected Output  ->  accepted formats: .txt, .docx, .pdf
   Describes expected behavior and outcomes used to generate assertions.

== GENERATED ARTIFACTS ==
- Cucumber .feature files (Gherkin BDD: Feature / Scenario / Given-When-Then)
- Java Page Object classes  (Selenium PageFactory + WebDriverWait)
- Step Definition Java classes  (@Given / @When / @Then annotations)
- Framework utilities: DriverFactory, ConfigReader, Hooks, TestRunner
- Full Maven project layout (pom.xml compatible)

== OUTPUT FOLDER STRUCTURE ==
src/test/java/pages/            -> Page Object classes (.java)
src/test/java/stepdefinitions/  -> Step Definition classes (.java)
src/test/java/utils/            -> DriverFactory, ConfigReader, Hooks (.java)
src/test/java/runners/          -> TestRunner (.java)
src/test/resources/features/    -> Cucumber .feature files

== TECH STACK ==
- Java 11+, Maven 3.6+
- Selenium WebDriver 4.x
- Cucumber 7.x (BDD)
- JUnit 5 for assertions
- WebDriverWait (no Thread.sleep)
- PageFactory pattern
- CSS selectors preferred; XPath only when necessary
- Chrome / ChromeDriver by default (configurable)

== HOW TO USE THE PLATFORM ==
1. Click "New Conversation" in the left sidebar to create a project.
2. In the right panel, upload all 3 required documents.
3. Click "Generate Code" — generation takes 30-60 seconds.
4. Click "Download All Files (ZIP)" to get the generated framework.
5. Extract the ZIP, then run:  mvn clean test

== RUNNING THE GENERATED TESTS ==
Prerequisites: Java JDK 11+, Maven 3.6+, Chrome + ChromeDriver on PATH
Run all tests:   mvn clean test
Run by tag:      mvn test -Dcucumber.filter.tags="@smoke"
Reports:         target/cucumber-reports/

== LIMITATIONS ==
- All 3 documents must be uploaded before clicking Generate.
- Tests are not executed inside the platform; you run them locally.
- Generated code targets Chrome by default.

Answer questions clearly and specifically based on this platform's actual capabilities.
If asked something unrelated to QA automation or this platform, politely redirect the user."""

    try:
        response = openai_client.generate_with_system_prompt(
            system_prompt, request.message, temperature=0.7, max_tokens=600
        )
        if not response:
            response = (
                "I'm having trouble reaching the AI right now. "
                "Please make sure the backend is running and try again."
            )
        return {"response": response}
    except Exception as e:
        logger.error(f"Chat endpoint error: {str(e)}")
        return {"response": "Sorry, an error occurred processing your message. Please try again."}
