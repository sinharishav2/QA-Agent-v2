from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import sys

# Configure logging FIRST so all initialization messages are captured
logger.remove()
logger.add(sys.stdout, level="INFO")

from config import settings
from api.routes import router, set_orchestrator

# Try to import database, but handle gracefully if psycopg2 is not available
try:
    from models.database import Base, engine
    db_available = True
except (ImportError, ModuleNotFoundError) as e:
    logger.warning(f"Database import failed: {str(e)}")
    logger.info("Running in demo mode without database")
    Base = None
    engine = None
    db_available = False

from agents.document_ingestion_agent import DocumentIngestionAgent
from agents.document_parser_agent import DocumentParserAgent
from agents.requirement_extraction_agent import RequirementExtractionAgent
from agents.test_case_extraction_agent import TestCaseExtractionAgent
from agents.test_design_agent import TestDesignAgent
from agents.test_data_agent import TestDataAgent
from agents.automation_framework_agent import AutomationFrameworkAgent
from agents.bdd_generator_agent import BDDGeneratorAgent
from agents.page_object_agent import PageObjectAgent
from agents.step_definition_agent import StepDefinitionAgent
from agents.locator_intelligence_agent import LocatorIntelligenceAgent
from agents.utility_generator_agent import UtilityGeneratorAgent
from orchestrator.orchestrator_agent import OrchestratorAgent

app = FastAPI(
    title="QA AI Automation Platform",
    description="AI-Powered QA Automation Agent System",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if db_available and Base is not None and engine is not None:
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.warning(f"Could not initialize database: {str(e)}")
        logger.info("Running in demo mode without database persistence")
else:
    logger.info("Database not available - running in demo mode with in-memory storage")

orchestrator = OrchestratorAgent()

document_ingestion_agent = DocumentIngestionAgent()
document_parser_agent = DocumentParserAgent()
requirement_extraction_agent = RequirementExtractionAgent()
test_case_extraction_agent = TestCaseExtractionAgent()
test_design_agent = TestDesignAgent()
test_data_agent = TestDataAgent()
automation_framework_agent = AutomationFrameworkAgent()
bdd_generator_agent = BDDGeneratorAgent()
page_object_agent = PageObjectAgent()
step_definition_agent = StepDefinitionAgent()
locator_intelligence_agent = LocatorIntelligenceAgent()
utility_generator_agent = UtilityGeneratorAgent()

orchestrator.register_agent("DocumentIngestionAgent", document_ingestion_agent)
orchestrator.register_agent("DocumentParserAgent", document_parser_agent)
orchestrator.register_agent("RequirementExtractionAgent", requirement_extraction_agent)
orchestrator.register_agent("TestCaseExtractionAgent", test_case_extraction_agent)
orchestrator.register_agent("TestDesignAgent", test_design_agent)
orchestrator.register_agent("TestDataAgent", test_data_agent)
orchestrator.register_agent("AutomationFrameworkAgent", automation_framework_agent)
orchestrator.register_agent("BDDGeneratorAgent", bdd_generator_agent)
orchestrator.register_agent("PageObjectAgent", page_object_agent)
orchestrator.register_agent("StepDefinitionAgent", step_definition_agent)
orchestrator.register_agent("LocatorIntelligenceAgent", locator_intelligence_agent)
orchestrator.register_agent("UtilityGeneratorAgent", utility_generator_agent)

# Inject the configured orchestrator into routes
set_orchestrator(orchestrator)

app.include_router(router)

@app.on_event("startup")
async def startup_event():
    logger.info("QA AI Automation Platform starting up...")
    logger.info(f"Environment: {settings.fastapi_env}")
    logger.info(f"Debug mode: {settings.fastapi_debug}")
    
    # Load persisted data
    from api.routes import load_storage
    load_storage()

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("QA AI Automation Platform shutting down...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.fastapi_host,
        port=settings.fastapi_port
    )
