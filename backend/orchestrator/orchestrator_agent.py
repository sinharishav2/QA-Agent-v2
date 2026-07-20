from typing import Dict, Any, List, Optional
from loguru import logger
import uuid
from datetime import datetime


class OrchestratorAgent:
    def __init__(self):
        self.agent_name = "OrchestratorAgent"
        self.logger = logger
        self.workflow_state = {}
        self.agent_registry = {}

    def register_agent(self, agent_name: str, agent_instance: Any):
        self.agent_registry[agent_name] = agent_instance
        self.logger.info(f"Agent registered: {agent_name}")

    def execute_workflow(self, workflow_id: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            self.logger.info(f"Starting workflow: {workflow_id}")
            self.workflow_state[workflow_id] = {
                "status": "in_progress",
                "start_time": datetime.utcnow(),
                "steps": []
            }

            project_id = input_data.get('project_id')
            documents = input_data.get('documents', [])

            parsed_documents = self._execute_document_parsing(workflow_id, documents)
            # Combine all document content for LLM context
            document_content = self._extract_combined_content(parsed_documents)
            requirements = self._execute_requirement_extraction(workflow_id, parsed_documents)
            test_cases = self._execute_test_case_extraction(workflow_id, parsed_documents)
            test_designs = self._execute_test_design(workflow_id, test_cases)
            test_data = self._execute_test_data_generation(workflow_id, test_cases)
            framework = self._execute_framework_selection(workflow_id, project_id)
            feature_files = self._execute_bdd_generation(workflow_id, test_cases, document_content)
            page_objects = self._execute_page_object_generation(workflow_id, test_cases, document_content)
            step_definitions = self._execute_step_definition_generation(workflow_id, feature_files, page_objects)
            locators = self._execute_locator_intelligence(workflow_id, page_objects)
            utilities = self._execute_utility_generation(workflow_id, framework)

            output_data = {
                "workflow_id": workflow_id,
                "project_id": project_id,
                "status": "completed",
                "parsed_documents": parsed_documents,
                "requirements": requirements,
                "test_cases": test_cases,
                "test_designs": test_designs,
                "test_data": test_data,
                "framework": framework,
                "feature_files": feature_files,
                "page_objects": page_objects,
                "step_definitions": step_definitions,
                "locators": locators,
                "utilities": utilities,
                "workflow_steps": self.workflow_state[workflow_id]["steps"]
            }

            self.workflow_state[workflow_id]["status"] = "completed"
            self.workflow_state[workflow_id]["end_time"] = datetime.utcnow()

            self.logger.info(f"Workflow completed: {workflow_id}")
            return output_data

        except Exception as e:
            self.logger.error(f"Workflow failed: {str(e)}")
            self.workflow_state[workflow_id]["status"] = "failed"
            self.workflow_state[workflow_id]["error"] = str(e)
            raise

    def _execute_document_parsing(self, workflow_id: str, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        self.logger.info(f"Executing document parsing for workflow {workflow_id}")
        print(f"Document parsing: received {len(documents)} documents")
        parsed_docs = []
        
        for doc in documents:
            agent = self.agent_registry.get("DocumentParserAgent")
            print(f"DocumentParserAgent from registry: {type(agent)}")
            if not agent:
                print("ERROR: DocumentParserAgent not found in registry!")
                continue
            try:
                print(f"Calling DocumentParserAgent.execute for doc: {doc.get('document_id')}, file: {doc.get('file_path')}")
                result = agent.execute(doc)
                print(f"DocumentParserAgent returned status: {result.get('status')}, error: {result.get('error', 'none')}")
                parsed_docs.append(result)
                self._log_step(workflow_id, "DocumentParsing", result.get('status', 'success'), result)
            except Exception as e:
                print(f"EXCEPTION in DocumentParserAgent.execute: {str(e)}")
                self.logger.error(f"Document parsing exception for {doc.get('document_id')}: {str(e)}", exc_info=True)
                parsed_docs.append({
                    "document_id": doc.get("document_id"),
                    "document_type": doc.get("document_type"),
                    "parsed_content": {"paragraphs": [], "lines": [], "content": "", "tables": [], "headings": []},
                    "status": "parse_failed"
                })

        self.logger.info(f"Document parsing complete: {len(parsed_docs)} documents parsed")
        return parsed_docs

    def _execute_requirement_extraction(self, workflow_id: str, parsed_documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        self.logger.info(f"Executing requirement extraction for workflow {workflow_id}")
        requirements = []

        for doc in parsed_documents:
            try:
                agent = self.agent_registry.get("RequirementExtractionAgent")
                if agent:
                    input_data = {
                        "document_id": doc.get("document_id"),
                        "parsed_content": doc.get("parsed_content", {})
                    }
                    result = agent.execute(input_data)
                    requirements.extend(result.get('requirements', []))
                    self._log_step(workflow_id, "RequirementExtraction", "success", result)
            except Exception as e:
                self.logger.error(f"Requirement extraction failed: {str(e)}")
                self._log_step(workflow_id, "RequirementExtraction", "failed", {"error": str(e)})

        return requirements

    def _execute_test_case_extraction(self, workflow_id: str, parsed_documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        self.logger.info(f"Executing test case extraction for workflow {workflow_id}")
        test_cases = []

        for doc in parsed_documents:
            try:
                agent = self.agent_registry.get("TestCaseExtractionAgent")
                if agent:
                    input_data = {
                        "document_id": doc.get("document_id"),
                        "parsed_content": doc.get("parsed_content", {})
                    }
                    result = agent.execute(input_data)
                    extracted = result.get('test_cases', [])
                    self.logger.info(f"Extracted {len(extracted)} test cases from document")
                    test_cases.extend(extracted)
                    self._log_step(workflow_id, "TestCaseExtraction", "success", result)
            except Exception as e:
                self.logger.error(f"Test case extraction failed: {str(e)}", exc_info=True)
                self._log_step(workflow_id, "TestCaseExtraction", "failed", {"error": str(e)})

        self.logger.info(f"Total test cases after extraction: {len(test_cases)}")
        return test_cases

    def _execute_test_design(self, workflow_id: str, test_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        self.logger.info(f"Executing test design for workflow {workflow_id}")
        try:
            agent = self.agent_registry.get("TestDesignAgent")
            if agent:
                result = agent.execute({"test_cases": test_cases})
                self._log_step(workflow_id, "TestDesign", "success", result)
                return result
        except Exception as e:
            self.logger.error(f"Test design failed: {str(e)}")
            self._log_step(workflow_id, "TestDesign", "failed", {"error": str(e)})
        return {}

    def _execute_test_data_generation(self, workflow_id: str, test_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        self.logger.info(f"Executing test data generation for workflow {workflow_id}")
        try:
            agent = self.agent_registry.get("TestDataAgent")
            if agent:
                result = agent.execute({"test_cases": test_cases})
                self._log_step(workflow_id, "TestDataGeneration", "success", result)
                return result
        except Exception as e:
            self.logger.error(f"Test data generation failed: {str(e)}")
            self._log_step(workflow_id, "TestDataGeneration", "failed", {"error": str(e)})
        return {}

    def _extract_combined_content(self, parsed_documents: List[Dict[str, Any]]) -> str:
        parts = []
        for doc in parsed_documents:
            content = doc.get('parsed_content', {})
            text = content.get('content', '')
            if not text:
                paragraphs = content.get('paragraphs', [])
                lines = content.get('lines', [])
                text = '\n'.join(paragraphs or lines)
            if text:
                parts.append(f"[{doc.get('document_type','document')}]\n{text}")
        return '\n\n'.join(parts)

    def _execute_framework_selection(self, workflow_id: str, project_id: str) -> Dict[str, Any]:
        self.logger.info(f"Executing framework selection for workflow {workflow_id}")
        try:
            agent = self.agent_registry.get("AutomationFrameworkAgent")
            if agent:
                result = agent.execute({"project_id": project_id, "preferred_framework": "java"})
                self._log_step(workflow_id, "FrameworkSelection", "success", result)
                return result
        except Exception as e:
            self.logger.error(f"Framework selection failed: {str(e)}")
            self._log_step(workflow_id, "FrameworkSelection", "failed", {"error": str(e)})
        return {}

    def _execute_bdd_generation(self, workflow_id: str, test_cases: List[Dict[str, Any]], document_content: str = '') -> List[Dict[str, Any]]:
        self.logger.info(f"Executing BDD generation for workflow {workflow_id}")
        try:
            agent = self.agent_registry.get("BDDGeneratorAgent")
            if agent:
                result = agent.execute({"test_cases": test_cases, "project_id": workflow_id, "document_content": document_content})
                self._log_step(workflow_id, "BDDGeneration", "success", result)
                return result.get('feature_files', [])
        except Exception as e:
            self.logger.error(f"BDD generation failed: {str(e)}")
            self._log_step(workflow_id, "BDDGeneration", "failed", {"error": str(e)})
        return []

    def _execute_page_object_generation(self, workflow_id: str, test_cases: List[Dict[str, Any]], document_content: str = '') -> List[Dict[str, Any]]:
        self.logger.info(f"Executing page object generation for workflow {workflow_id}")
        try:
            agent = self.agent_registry.get("PageObjectAgent")
            if agent:
                result = agent.execute({"test_cases": test_cases, "project_id": workflow_id, "document_content": document_content})
                self._log_step(workflow_id, "PageObjectGeneration", "success", result)
                return result.get('page_objects', [])
        except Exception as e:
            self.logger.error(f"Page object generation failed: {str(e)}")
            self._log_step(workflow_id, "PageObjectGeneration", "failed", {"error": str(e)})
        return []

    def _execute_step_definition_generation(self, workflow_id: str, feature_files: List[Dict[str, Any]], page_objects: List[Dict[str, Any]] = []) -> List[Dict[str, Any]]:
        self.logger.info(f"Executing step definition generation for workflow {workflow_id}")
        try:
            agent = self.agent_registry.get("StepDefinitionAgent")
            if agent:
                result = agent.execute({"feature_files": feature_files, "project_id": workflow_id, "page_objects": page_objects})
                self._log_step(workflow_id, "StepDefinitionGeneration", "success", result)
                return result.get('step_definitions', [])
        except Exception as e:
            self.logger.error(f"Step definition generation failed: {str(e)}")
            self._log_step(workflow_id, "StepDefinitionGeneration", "failed", {"error": str(e)})
        return []

    def _execute_locator_intelligence(self, workflow_id: str, page_objects: List[Dict[str, Any]]) -> Dict[str, Any]:
        self.logger.info(f"Executing locator intelligence for workflow {workflow_id}")
        try:
            agent = self.agent_registry.get("LocatorIntelligenceAgent")
            if agent:
                result = agent.execute({"page_objects": page_objects, "project_id": workflow_id})
                self._log_step(workflow_id, "LocatorIntelligence", "success", result)
                return result.get('locators', {})
        except Exception as e:
            self.logger.error(f"Locator intelligence failed: {str(e)}")
            self._log_step(workflow_id, "LocatorIntelligence", "failed", {"error": str(e)})
        return {}

    def _execute_utility_generation(self, workflow_id: str, framework: Dict[str, Any]) -> Dict[str, Any]:
        self.logger.info(f"Executing utility generation for workflow {workflow_id}")
        try:
            agent = self.agent_registry.get("UtilityGeneratorAgent")
            if agent:
                result = agent.execute({"project_id": workflow_id, "framework": framework.get('selected_framework', 'python')})
                self._log_step(workflow_id, "UtilityGeneration", "success", result)
                return result.get('utilities', {})
        except Exception as e:
            self.logger.error(f"Utility generation failed: {str(e)}")
            self._log_step(workflow_id, "UtilityGeneration", "failed", {"error": str(e)})
        return {}

    def _log_step(self, workflow_id: str, step_name: str, status: str, result: Dict[str, Any]):
        step_record = {
            "step_name": step_name,
            "status": status,
            "timestamp": datetime.utcnow().isoformat(),
            "result": result
        }
        self.workflow_state[workflow_id]["steps"].append(step_record)
        self.logger.info(f"Step logged: {step_name} - {status}")

    def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        return self.workflow_state.get(workflow_id, {})
