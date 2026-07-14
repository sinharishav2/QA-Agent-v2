from .base_agent import BaseAgent
from typing import Dict, Any, List
import uuid


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
            output_data = {"error": str(e), "status": "failed"}
            self.log_execution(input_data, output_data, status="failed", error=str(e))
            raise

    def _extract_test_cases(self, parsed_content: Dict[str, Any]) -> List[Dict[str, Any]]:
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
