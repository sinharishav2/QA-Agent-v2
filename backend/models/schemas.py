from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class DocumentType(str, Enum):
    FUNCTIONAL_SPEC = "functional_specification"
    TEST_CASES = "test_cases"
    EXPECTED_OUTPUT = "expected_output"


class DocumentUploadRequest(BaseModel):
    document_type: DocumentType
    project_id: str


class DocumentReference(BaseModel):
    document_id: str
    document_type: DocumentType
    filename: str
    upload_timestamp: datetime
    file_path: str


class ParsedDocument(BaseModel):
    document_id: str
    sections: List[Dict[str, Any]] = []
    tables: List[Dict[str, Any]] = []
    headings: List[str] = []
    paragraphs: List[str] = []


class Requirement(BaseModel):
    requirement_id: str
    feature: str
    business_rules: List[str] = []
    workflows: List[str] = []
    validations: List[str] = []
    preconditions: List[str] = []
    dependencies: List[str] = []


class TestCase(BaseModel):
    test_id: str
    scenario: str
    preconditions: List[str] = []
    steps: List[str] = []
    expected_results: List[str] = []
    test_data: Dict[str, Any] = {}
    priority: str = "medium"
    module: str


class TestDesignOutput(BaseModel):
    positive_tests: List[TestCase] = []
    negative_tests: List[TestCase] = []
    boundary_tests: List[TestCase] = []
    equivalence_partitions: List[Dict[str, Any]] = []
    error_handling: List[Dict[str, Any]] = []
    smoke_tests: List[TestCase] = []
    sanity_tests: List[TestCase] = []
    regression_tests: List[TestCase] = []


class TestDataSet(BaseModel):
    valid_data: List[Dict[str, Any]] = []
    invalid_data: List[Dict[str, Any]] = []
    boundary_data: List[Dict[str, Any]] = []
    null_data: List[Dict[str, Any]] = []
    random_data: List[Dict[str, Any]] = []
    security_data: List[Dict[str, Any]] = []


class PageObject(BaseModel):
    page_name: str
    elements: Dict[str, Dict[str, str]] = {}
    methods: List[str] = []


class StepDefinition(BaseModel):
    step_text: str
    implementation: str
    page_objects_used: List[str] = []


class FeatureFile(BaseModel):
    feature_name: str
    scenarios: List[Dict[str, Any]] = []
    background: Optional[str] = None


class AutomationTestModel(BaseModel):
    project_id: str
    requirements: List[Requirement] = []
    test_cases: List[TestCase] = []
    locators: Dict[str, Dict[str, str]] = {}
    pages: List[PageObject] = []
    assertions: List[Dict[str, Any]] = []
    business_rules: List[str] = []
    generated_scripts: List[str] = []
    metadata: Dict[str, Any] = {}


class ExecutionResult(BaseModel):
    test_id: str
    status: str
    execution_time: float
    screenshots: List[str] = []
    logs: List[str] = []
    console_errors: List[str] = []
    network_logs: List[str] = []


class ExecutionReport(BaseModel):
    project_id: str
    total_tests: int
    passed: int
    failed: int
    skipped: int
    execution_time: float
    results: List[ExecutionResult] = []
    timestamp: datetime


class Project(BaseModel):
    project_id: str
    project_name: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    status: str = "draft"
    automation_framework: Optional[str] = None
    documents: List[DocumentReference] = []
