from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import re
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
            "manual_test_cases_count": result.get('manual_test_cases_count', len(result.get('test_cases', []))),
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

        feature_files    = result.get('feature_files', [])
        page_objects     = result.get('page_objects', [])
        step_definitions = result.get('step_definitions', [])
        test_cases       = result.get('test_cases', [])
        requirements     = result.get('requirements', [])
        utilities        = result.get('utilities', {})

        # Manual test cases = only those extracted from the 'test_cases' document
        parsed_count = result.get('manual_test_cases_count', len(test_cases))

        # Generated test scripts = 1 automation script per manual test case (excludes helper classes / feature splits)
        generated_scripts = parsed_count

        logger.info(f"Automation generated for project: {project_id}")
        return {
            "workflow_id": workflow_id,
            "project_id": project_id,
            "status": "completed",
            "framework": result.get('framework'),
            "total_test_cases":              parsed_count,       # backwards-compat
            "total_parsed_test_cases":       parsed_count,       # manual, from test_cases document
            "total_generated_test_scripts":  generated_scripts,  # automation scripts produced
            "total_features":        len(feature_files),
            "total_pages":           len(page_objects),
            "total_step_definitions": len(step_definitions),
            "total_utilities":       len(utilities) if isinstance(utilities, dict) else 0,
            "total_requirements":    len(requirements),
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


def _build_html_report(project_id: str, artifacts: dict, documents: list, project: dict) -> str:
    """Build a self-contained HTML quality report for the generated artifacts."""
    from datetime import datetime as _dt
    quality = artifacts.get('quality_metrics', {})
    feature_files   = artifacts.get('feature_files', [])
    page_objects    = artifacts.get('page_objects', [])
    step_defs       = artifacts.get('step_definitions', [])
    test_cases      = artifacts.get('test_cases', [])
    utilities       = artifacts.get('utilities', {})
    requirements    = artifacts.get('requirements', [])
    framework       = artifacts.get('framework', {})
    # Derive the same counts used in the generate response
    _manual_count      = artifacts.get('manual_test_cases_count', len(test_cases))
    _generated_scripts = _manual_count

    overall       = quality.get('overall_score', 'N/A')
    score_color   = '#22c55e' if isinstance(overall, (int,float)) and overall >= 80 else ('#f59e0b' if isinstance(overall, (int,float)) and overall >= 60 else '#ef4444')

    def score_badge(label, key):
        val = quality.get(key, 'N/A')
        color = '#22c55e' if isinstance(val,(int,float)) and val>=80 else ('#f59e0b' if isinstance(val,(int,float)) and val>=60 else '#ef4444')
        return f'<tr><td>{label}</td><td><span style="background:{color};color:#fff;padding:2px 10px;border-radius:12px;font-weight:600">{val}/100</span></td></tr>'

    def file_list(items, name_key='filename'):
        if not items:
            return '<li><em>None generated</em></li>'
        return ''.join(f'<li><code>{i.get(name_key, "unknown")}</code></li>' for i in items)

    util_names = [v.get('filename', k) for k, v in utilities.items() if isinstance(v, dict)] if isinstance(utilities, dict) else []
    input_files = [d.get('filename', d.get('document_type', 'unknown')) for d in documents]
    suggestions = quality.get('improvement_suggestions', [])
    critical    = quality.get('critical_issues', [])
    strengths   = []
    if isinstance(overall,(int,float)) and overall >= 80: strengths.append('High overall quality score')
    if quality.get('traceability', 0) >= 70: strengths.append('Good requirement traceability via @req-* tags')
    if quality.get('assertion_quality', 0) >= 70: strengths.append('Assertions present in step definitions')
    if quality.get('framework_structure', 0) >= 70: strengths.append('Framework structure is well organized')
    if not strengths: strengths = ['Automation framework generated successfully']

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>QA Agent v2 — Generation Report</title>
<style>
  body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;margin:0;background:#f8fafc;color:#1e293b}}
  .header{{background:linear-gradient(135deg,#1e3a5f,#2563eb);color:#fff;padding:32px 40px}}
  .header h1{{margin:0 0 6px;font-size:1.8rem}}
  .header p{{margin:0;opacity:.8;font-size:.95rem}}
  .container{{max-width:960px;margin:32px auto;padding:0 24px}}
  .grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:16px;margin-bottom:32px}}
  .card{{background:#fff;border-radius:10px;padding:20px;box-shadow:0 1px 4px rgba(0,0,0,.08);text-align:center}}
  .card .num{{font-size:2rem;font-weight:700;color:#2563eb}}
  .card .lbl{{font-size:.8rem;color:#64748b;margin-top:4px}}
  .score-card{{background:#fff;border-radius:10px;padding:24px;box-shadow:0 1px 4px rgba(0,0,0,.08);margin-bottom:24px;text-align:center}}
  .score-card .big{{font-size:4rem;font-weight:800;color:{score_color}}}
  .score-card .lbl{{color:#64748b;font-size:.9rem}}
  section{{background:#fff;border-radius:10px;padding:24px;box-shadow:0 1px 4px rgba(0,0,0,.08);margin-bottom:24px}}
  section h2{{margin:0 0 16px;font-size:1.1rem;color:#1e3a5f;border-bottom:2px solid #e2e8f0;padding-bottom:8px}}
  table{{width:100%;border-collapse:collapse}}
  td,th{{padding:8px 12px;text-align:left;border-bottom:1px solid #f1f5f9}}
  th{{font-weight:600;color:#475569;font-size:.85rem}}
  ul{{margin:0;padding-left:20px;line-height:1.8}}
  code{{background:#f1f5f9;padding:1px 6px;border-radius:4px;font-size:.88rem}}
  .tag{{display:inline-block;padding:2px 8px;border-radius:10px;font-size:.78rem;font-weight:600}}
  .green{{background:#dcfce7;color:#166534}}
  .red{{background:#fee2e2;color:#991b1b}}
  .amber{{background:#fef3c7;color:#92400e}}
  footer{{text-align:center;color:#94a3b8;font-size:.8rem;padding:24px}}
</style>
</head>
<body>
<div class="header">
  <h1>QA Agent v2 — Generation Report</h1>
  <p>Project ID: {project_id} &nbsp;|&nbsp; Generated: {_dt.utcnow().strftime('%Y-%m-%d %H:%M')} UTC &nbsp;|&nbsp; Framework: {framework.get('selected_framework','Java').upper()} + Selenium + Cucumber</p>
</div>
<div class="container">

<div class="grid">
  <div class="card"><div class="num">{len(requirements)}</div><div class="lbl">Requirements</div></div>
  <div class="card"><div class="num">{_manual_count}</div><div class="lbl">Test Cases Parsed</div></div>
  <div class="card"><div class="num">{_generated_scripts}</div><div class="lbl">Generated Test Scripts</div></div>
  <div class="card"><div class="num">{len(feature_files)}</div><div class="lbl">Feature Files</div></div>
  <div class="card"><div class="num">{len(page_objects)}</div><div class="lbl">Page Objects</div></div>
  <div class="card"><div class="num">{len(step_defs)}</div><div class="lbl">Step Def Classes</div></div>
  <div class="card"><div class="num">{len(util_names)}</div><div class="lbl">Utility Files</div></div>
</div>

<div class="score-card">
  <div class="big">{overall}<span style="font-size:1.5rem;color:#94a3b8">/100</span></div>
  <div class="lbl">Overall Quality Score</div>
  <p style="color:{score_color};font-weight:600;margin:8px 0 0">{quality.get('summary','')}</p>
</div>

<section>
  <h2>Quality Metrics</h2>
  <table><thead><tr><th>Dimension</th><th>Score</th></tr></thead><tbody>
  {score_badge('Gherkin Quality','gherkin_quality')}
  {score_badge('Java Code Quality','java_code_quality')}
  {score_badge('Step Definition Coverage','step_definition_coverage')}
  {score_badge('Page Object Quality','page_object_quality')}
  {score_badge('Locator Quality','locator_quality')}
  {score_badge('Framework Structure','framework_structure')}
  {score_badge('Traceability','traceability')}
  {score_badge('Assertion Quality','assertion_quality')}
  {score_badge('Maintainability','maintainability')}
  {score_badge('Automation Readiness','automation_readiness')}
  </tbody></table>
</section>

<section>
  <h2>Generated Artifacts</h2>
  <table>
    <tr><th>Type</th><th>Files</th></tr>
    <tr><td>Feature Files</td><td><ul>{ ''.join(f'<li><code>{f.get("filename","?")}</code></li>' for f in feature_files) or '<li><em>None</em></li>' }</ul></td></tr>
    <tr><td>Page Objects</td><td><ul>{ ''.join(f'<li><code>{p.get("filename","?")}</code></li>' for p in page_objects) or '<li><em>None</em></li>' }</ul></td></tr>
    <tr><td>Step Definitions</td><td><ul>{ ''.join(f'<li><code>{s.get("filename","?")}</code></li>' for s in step_defs) or '<li><em>None</em></li>' }</ul></td></tr>
    <tr><td>Utilities</td><td><ul>{ ''.join(f'<li><code>{n}</code></li>' for n in util_names) or '<li><em>None</em></li>' }</ul></td></tr>
  </table>
</section>

<section style="display:grid;grid-template-columns:1fr 1fr;gap:24px">
  <div>
    <h2 style="margin-top:0">Key Strengths</h2>
    <ul>{''.join(f'<li class="tag green" style="margin:4px 0;display:list-item;background:none;color:inherit">✓ {s}</li>' for s in strengths)}</ul>
  </div>
  <div>
    <h2 style="margin-top:0">Improvement Areas</h2>
    <ul>{''.join(f'<li style="margin:4px 0;color:#b45309">{s}</li>' for s in (suggestions or ['No suggestions — code looks good!']))}</ul>
  </div>
</section>

{'<section><h2>Critical Issues</h2><ul>' + ''.join(f'<li class="tag red" style="background:none;color:#b91c1c;display:list-item;margin:4px 0">⚠ {c}</li>' for c in critical) + '</ul></section>' if critical else ''}

<section>
  <h2>Input Files Used</h2>
  <ul>{''.join(f'<li><code>{f}</code></li>' for f in input_files) if input_files else '<li><em>No uploaded files recorded</em></li>'}</ul>
</section>

<section>
  <h2>Running the Tests</h2>
  <pre style="background:#0f172a;color:#e2e8f0;padding:16px;border-radius:8px;overflow-x:auto;font-size:.88rem"># Run all tests
mvn clean test

# Run by tag
mvn test -Dcucumber.filter.tags="@smoke"

# Reports will be generated at: target/cucumber-reports/</pre>
</section>

</div>
<footer>Generated by QA Agent v2 — {_dt.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC</footer>
</body></html>"""
    return html


@router.get("/projects/{project_id}/download")
async def download_generated_files(project_id: str):
    try:
        if project_id not in projects_store:
            raise HTTPException(status_code=404, detail="Project not found")

        artifacts = projects_store[project_id].get("generated_artifacts")
        if not artifacts:
            raise HTTPException(status_code=404, detail="No generated files found. Please generate first.")

        documents = documents_store.get(project_id, [])
        project   = projects_store[project_id]

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            written_paths: set = set()

            def _basename(path: str) -> str:
                return path.replace('\\', '/').split('/')[-1]

            def _write(dest: str, content: str) -> None:
                """Write to ZIP only if path not already present (prevents duplicate entries)."""
                if dest in written_paths:
                    logger.warning(f"Skipping duplicate ZIP entry: {dest}")
                    return
                zip_file.writestr(dest, content)
                written_paths.add(dest)

            # Feature files (BDD .feature)
            for i, feature in enumerate(artifacts.get('feature_files', [])):
                content  = feature.get('content') or feature.get('feature_content') or json.dumps(feature, indent=2)
                filename = _basename(feature.get('filename') or f'feature_{i+1}.feature')
                _write(f"src/test/resources/features/{filename}", content)

            # Page objects
            for i, page in enumerate(artifacts.get('page_objects', [])):
                content  = page.get('content') or page.get('class_content') or json.dumps(page, indent=2)
                filename = _basename(page.get('filename') or f'Page_{i+1}.java')
                _write(f"src/test/java/pages/{filename}", content)

            # Step definitions
            for i, step in enumerate(artifacts.get('step_definitions', [])):
                content  = step.get('content') or step.get('step_content') or json.dumps(step, indent=2)
                filename = _basename(step.get('filename') or f'StepDefs_{i+1}.java')
                _write(f"src/test/java/stepdefinitions/{filename}", content)

            # Test cases as JSON
            test_cases = artifacts.get('test_cases', [])
            if test_cases:
                _write("test_cases.json", json.dumps(test_cases, indent=2))

            # Framework utility files — use zip_path if provided for correct folder placement
            utilities = artifacts.get('utilities', {})
            if isinstance(utilities, dict):
                for util_name, util_data in utilities.items():
                    if isinstance(util_data, dict) and util_data.get('content'):
                        filename = util_data.get('filename', f'{util_name}.java')
                        zip_path = util_data.get('zip_path')
                        if zip_path:
                            dest = zip_path.replace('\\', '/')
                        else:
                            ext = filename.rsplit('.', 1)[-1] if '.' in filename else 'java'
                            if ext == 'xml' and filename == 'pom.xml':
                                dest = filename
                            elif ext in ('properties', 'xml'):
                                dest = f"src/test/resources/{filename}"
                            else:
                                dest = f"src/test/java/utils/{filename}"
                        _write(dest, util_data['content'])

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
            _write("summary.json", json.dumps(summary, indent=2))

            # Traceability map
            traceability_map = artifacts.get('traceability_map', {})
            if traceability_map:
                _write("traceability.json", json.dumps(traceability_map, indent=2))

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
            _write("README.md", readme_content)

            # HTML quality report
            html_report = _build_html_report(project_id, artifacts, documents, project)
            _write("report.html", html_report)

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


@router.get("/projects/{project_id}/report")
async def download_html_report(project_id: str):
    """Return the HTML quality report as a downloadable file."""
    try:
        if project_id not in projects_store:
            raise HTTPException(status_code=404, detail="Project not found")
        artifacts = projects_store[project_id].get("generated_artifacts")
        if not artifacts:
            raise HTTPException(status_code=404, detail="No generated files found. Please generate first.")
        documents = documents_store.get(project_id, [])
        project   = projects_store[project_id]
        html = _build_html_report(project_id, artifacts, documents, project)
        from fastapi.responses import HTMLResponse
        return HTMLResponse(
            content=html,
            headers={"Content-Disposition": f"attachment; filename=qa_report_{project_id[:8]}.html"}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}", exc_info=True)
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
