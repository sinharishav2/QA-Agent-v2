from .base_agent import BaseAgent
from typing import Dict, Any, List
import uuid
from utils.openai_client import openai_client


class TestCaseExtractionAgent(BaseAgent):
    def __init__(self):
        super().__init__("TestCaseExtractionAgent")
        print("TestCaseExtractionAgent initialized")

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        print(f"TestCaseExtractionAgent.execute called")
        try:
            self.logger.info(f"TestCaseExtractionAgent.execute called with input keys: {input_data.keys()}")
            
            if not self.validate_input(input_data, ['document_id', 'parsed_content']):
                raise ValueError("Missing required input fields")

            document_id = input_data['document_id']
            parsed_content = input_data['parsed_content']
            
            self.logger.info(f"Extracting test cases for document: {document_id}")

            test_cases = self._extract_test_cases(parsed_content)
            self.logger.info(f"_extract_test_cases returned {len(test_cases)} test cases")
            
            # Return whatever was extracted - don't use defaults
            # This ensures we only return LLM-generated content from user documents

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
            self.logger.error(f"Test case extraction failed: {str(e)}", exc_info=True)
            # Return empty test cases on error - don't use defaults
            output_data = {
                "document_id": input_data.get('document_id'),
                "test_cases": [],
                "total_test_cases": 0,
                "status": "failed",
                "error": str(e)
            }
            self.log_execution(input_data, output_data, status="failed", error=str(e))
            return output_data

    def _extract_test_cases(self, parsed_content: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract test cases from document content using LLM"""
        print("_extract_test_cases called")
        self.logger.info("Starting test case extraction from document")
        test_cases = []
        
        # Prepare content from the document
        content_text = self._prepare_content_text(parsed_content)
        print(f"Content length: {len(content_text)}")
        self.logger.info(f"Document content length: {len(content_text)}")
        self.logger.info(f"Content preview: {content_text[:500]}")
        
        if len(content_text.strip()) > 0:
            # Try to extract using OpenAI/Azure
            try:
                self.logger.info("Calling openai_client.extract_test_cases...")
                openai_response = openai_client.extract_test_cases(content_text)
                self.logger.info(f"OpenAI response type: {type(openai_response)}")
                self.logger.info(f"OpenAI response: {openai_response}")
                
                if openai_response and len(openai_response.strip()) > 0:
                    self.logger.info(f"OpenAI returned response of length: {len(openai_response)}")
                    test_cases = self._parse_openai_test_cases(openai_response)
                    self.logger.info(f"Parsed {len(test_cases)} test cases from OpenAI")
                else:
                    self.logger.warning("OpenAI returned empty response")
            except Exception as e:
                self.logger.error(f"OpenAI extraction error: {str(e)}", exc_info=True)
        else:
            self.logger.warning("Document content is empty")
        
        self.logger.info(f"Total test cases extracted: {len(test_cases)}")
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
        
        self.logger.info(f"Parsing OpenAI response of length {len(openai_response)}")
        
        # Try to parse JSON first (if LLM returned JSON format)
        try:
            import json
            # Look for JSON array in the response
            if '[' in openai_response and ']' in openai_response:
                json_start = openai_response.find('[')
                json_end = openai_response.rfind(']') + 1
                json_str = openai_response[json_start:json_end]
                parsed = json.loads(json_str)
                
                if isinstance(parsed, list):
                    for item in parsed:
                        test_case = {
                            "test_id": item.get('testCaseId') or item.get('test_id') or f"TC-{len(test_cases)+1}",
                            "scenario": item.get('description') or item.get('scenario') or "",
                            "preconditions": item.get('preconditions') or [],
                            "steps": item.get('steps') or [],
                            "expected_results": item.get('expectedResults') or item.get('expected_results') or [],
                            "test_data": item.get('testData') or item.get('test_data') or {},
                            "priority": item.get('priority') or "medium",
                            "module": item.get('module') or "general"
                        }
                        test_cases.append(test_case)
                    self.logger.info(f"Parsed {len(test_cases)} test cases from JSON")
                    return test_cases
        except Exception as e:
            self.logger.debug(f"JSON parsing failed: {str(e)}, trying text parsing")
        
        # Fallback to text parsing
        lines = openai_response.split('\n')
        current_tc = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if line.startswith('TC-') or line.startswith('**TC-'):
                if current_tc:
                    test_cases.append(current_tc)
                
                # Extract test ID and scenario
                clean_line = line.replace('**', '')
                if ':' in clean_line:
                    parts = clean_line.split(':', 1)
                    test_id = parts[0].strip()
                    scenario = parts[1].strip() if len(parts) > 1 else ""
                else:
                    test_id = clean_line
                    scenario = ""
                
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
            elif current_tc:
                if line.startswith('Scenario:'):
                    current_tc["scenario"] = line.replace('Scenario:', '').strip()
                elif line.startswith('Preconditions:') or line.startswith('- '):
                    if line.startswith('- '):
                        current_tc["preconditions"].append(line[2:].strip())
                elif line.startswith('Steps:'):
                    pass  # Skip header
                elif line.startswith('1.') or line.startswith('2.') or line.startswith('3.'):
                    current_tc["steps"].append(line.split('.', 1)[1].strip() if '.' in line else line)
                elif line.startswith('Expected'):
                    pass  # Skip header
        
        if current_tc:
            test_cases.append(current_tc)
        
        self.logger.info(f"Parsed {len(test_cases)} test cases from text")
        return test_cases
    
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
