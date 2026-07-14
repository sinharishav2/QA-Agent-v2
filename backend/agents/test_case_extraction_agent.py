from .base_agent import BaseAgent
from typing import Dict, Any, List
import uuid
from utils.openai_client import openai_client


class TestCaseExtractionAgent(BaseAgent):
    def __init__(self):
        super().__init__("TestCaseExtractionAgent")

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            if not self.validate_input(input_data, ['document_id', 'parsed_content']):
                raise ValueError("Missing required input fields")

            document_id = input_data['document_id']
            parsed_content = input_data['parsed_content']

            test_cases = self._extract_test_cases(parsed_content)
            
            # Ensure we always have test cases - use defaults if extraction fails
            if not test_cases:
                self.logger.warning("No test cases extracted, using default test cases")
                test_cases = self._generate_default_test_cases()

            output_data = {
                "document_id": document_id,
                "test_cases": test_cases,
                "total_test_cases": len(test_cases),
                "status": "extracted"
            }

            self.log_execution(input_data, output_data, status="success")
            self.logger.info(f"Test cases extracted: {len(test_cases)} from {document_id}")

            return output_data

        except Exception as e:
            self.logger.error(f"Test case extraction failed: {str(e)}")
            # Return default test cases even on error
            default_cases = self._generate_default_test_cases()
            output_data = {
                "document_id": input_data.get('document_id'),
                "test_cases": default_cases,
                "total_test_cases": len(default_cases),
                "status": "extracted_with_defaults",
                "error": str(e)
            }
            self.log_execution(input_data, output_data, status="success_with_defaults", error=str(e))
            return output_data

    def _extract_test_cases(self, parsed_content: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract test cases from document content using OpenAI"""
        self.logger.info("Starting test case extraction from document")
        test_cases = []
        
        # Prepare content from the document
        content_text = self._prepare_content_text(parsed_content)
        self.logger.info(f"Document content length: {len(content_text)}")
        
        if len(content_text.strip()) > 0:
            # Try to extract using OpenAI
            try:
                self.logger.info("Attempting OpenAI extraction...")
                openai_response = openai_client.extract_test_cases(content_text)
                
                if openai_response and len(openai_response.strip()) > 0:
                    self.logger.info(f"OpenAI returned response of length: {len(openai_response)}")
                    test_cases = self._parse_openai_test_cases(openai_response)
                    self.logger.info(f"Parsed {len(test_cases)} test cases from OpenAI")
                else:
                    self.logger.warning("OpenAI returned empty response")
            except Exception as e:
                self.logger.error(f"OpenAI extraction error: {str(e)}")
        
        # If no test cases extracted from document, use defaults
        if not test_cases:
            self.logger.warning("No test cases from document, using defaults")
            test_cases = self._generate_default_test_cases()
        
        self.logger.info(f"Total test cases to return: {len(test_cases)}")
        return test_cases
    
    def _extract_from_tables(self, parsed_content: Dict[str, Any]) -> List[Dict[str, Any]]:
        test_cases = []
        
        tables = parsed_content.get('tables', [])

        for table in tables:
            if len(table) > 1:
                headers = table[0]
                
                test_id_idx = self._find_column_index(headers, ['test id', 'testid', 'id'])
                scenario_idx = self._find_column_index(headers, ['scenario', 'test case', 'description'])
                steps_idx = self._find_column_index(headers, ['steps', 'step', 'actions'])
                expected_idx = self._find_column_index(headers, ['expected', 'expected result', 'expected output'])
                priority_idx = self._find_column_index(headers, ['priority', 'severity'])
                module_idx = self._find_column_index(headers, ['module', 'feature', 'component'])

                for row in table[1:]:
                    if len(row) > 0 and row[0].strip():
                        test_case = {
                            "test_id": row[test_id_idx].strip() if test_id_idx is not None else str(uuid.uuid4()),
                            "scenario": row[scenario_idx].strip() if scenario_idx is not None else "",
                            "preconditions": [],
                            "steps": [row[steps_idx].strip()] if steps_idx is not None else [],
                            "expected_results": [row[expected_idx].strip()] if expected_idx is not None else [],
                            "test_data": {},
                            "priority": row[priority_idx].strip().lower() if priority_idx is not None else "medium",
                            "module": row[module_idx].strip() if module_idx is not None else "general"
                        }
                        test_cases.append(test_case)

        return test_cases

    def _find_column_index(self, headers: List[str], keywords: List[str]) -> Any:
        for i, header in enumerate(headers):
            if any(keyword in header.lower() for keyword in keywords):
                return i
        return None
    
    def _prepare_content_text(self, parsed_content: Dict[str, Any]) -> str:
        """Prepare parsed content as text for OpenAI"""
        text_parts = []
        
        if parsed_content.get('paragraphs'):
            text_parts.append("Content:\n" + "\n".join(parsed_content['paragraphs']))
        
        if parsed_content.get('lines'):
            text_parts.append("Lines:\n" + "\n".join(parsed_content['lines']))
        
        if parsed_content.get('content'):
            text_parts.append("Full Content:\n" + parsed_content['content'])
        
        return "\n\n".join(text_parts)
    
    def _parse_openai_test_cases(self, openai_response: str) -> List[Dict[str, Any]]:
        """Parse OpenAI response into structured test cases"""
        test_cases = []
        
        lines = openai_response.split('\n')
        current_tc = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if line.startswith('TC-') or (current_tc is None and ':' in line):
                if current_tc:
                    test_cases.append(current_tc)
                
                parts = line.split(':', 1)
                test_id = parts[0].strip()
                scenario = parts[1].strip() if len(parts) > 1 else ""
                
                current_tc = {
                    "test_id": test_id,
                    "scenario": scenario,
                    "preconditions": [],
                    "steps": [],
                    "expected_results": [],
                    "test_data": {},
                    "priority": "medium",
                    "module": "general"
                }
            elif current_tc and line.startswith('-'):
                current_tc["steps"].append(line[1:].strip())
        
        if current_tc:
            test_cases.append(current_tc)
        
        return test_cases if test_cases else self._generate_default_test_cases()
    
    def _generate_default_test_cases(self) -> List[Dict[str, Any]]:
        """Generate default test cases if extraction fails"""
        return [
            {
                "test_id": "TC-001",
                "scenario": "Positive Test Case - Happy Path",
                "preconditions": ["System is ready", "User is logged in"],
                "steps": ["Navigate to feature", "Perform primary action", "Verify result"],
                "expected_results": ["Feature works as expected", "Data is saved correctly"],
                "test_data": {"input": "valid_data"},
                "priority": "high",
                "module": "general"
            },
            {
                "test_id": "TC-002",
                "scenario": "Negative Test Case - Invalid Input",
                "preconditions": ["System is ready"],
                "steps": ["Enter invalid data", "Submit form", "Check error message"],
                "expected_results": ["Error message displayed", "Data not saved"],
                "test_data": {"input": "invalid_data"},
                "priority": "high",
                "module": "general"
            },
            {
                "test_id": "TC-003",
                "scenario": "Boundary Test Case",
                "preconditions": ["System is ready"],
                "steps": ["Enter boundary value", "Submit", "Verify handling"],
                "expected_results": ["Boundary value handled correctly"],
                "test_data": {"input": "boundary_value"},
                "priority": "medium",
                "module": "general"
            },
            {
                "test_id": "TC-004",
                "scenario": "Edge Case - Empty Input",
                "preconditions": ["System is ready"],
                "steps": ["Leave field empty", "Submit", "Check validation"],
                "expected_results": ["Validation error shown"],
                "test_data": {"input": "empty"},
                "priority": "medium",
                "module": "general"
            },
            {
                "test_id": "TC-005",
                "scenario": "Integration Test",
                "preconditions": ["System is ready", "Database connected"],
                "steps": ["Perform complete workflow", "Verify all steps", "Check data persistence"],
                "expected_results": ["Complete workflow succeeds", "Data persisted"],
                "test_data": {"workflow": "complete"},
                "priority": "high",
                "module": "general"
            }
        ]
