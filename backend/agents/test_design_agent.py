from .base_agent import BaseAgent
from typing import Dict, Any, List
import uuid


class TestDesignAgent(BaseAgent):
    def __init__(self):
        super().__init__("TestDesignAgent")

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            if not self.validate_input(input_data, ['test_cases']):
                raise ValueError("Missing required input fields")

            test_cases = input_data['test_cases']

            positive_tests = self._generate_positive_tests(test_cases)
            negative_tests = self._generate_negative_tests(test_cases)
            boundary_tests = self._generate_boundary_tests(test_cases)
            smoke_tests = self._generate_smoke_tests(test_cases)
            sanity_tests = self._generate_sanity_tests(test_cases)
            regression_tests = self._generate_regression_tests(test_cases)

            output_data = {
                "positive_tests": positive_tests,
                "negative_tests": negative_tests,
                "boundary_tests": boundary_tests,
                "equivalence_partitions": [],
                "error_handling": [],
                "smoke_tests": smoke_tests,
                "sanity_tests": sanity_tests,
                "regression_tests": regression_tests,
                "total_designed_tests": len(positive_tests) + len(negative_tests) + len(boundary_tests),
                "status": "designed"
            }

            self.log_execution(input_data, output_data, status="success")
            self.logger.info(f"Test design completed with {output_data['total_designed_tests']} tests")

            return output_data

        except Exception as e:
            self.logger.error(f"Test design failed: {str(e)}")
            output_data = {"error": str(e), "status": "failed"}
            self.log_execution(input_data, output_data, status="failed", error=str(e))
            raise

    def _generate_positive_tests(self, test_cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        positive_tests = []
        for tc in test_cases:
            positive_test = {
                "test_id": f"{tc.get('test_id', 'TC')}_POS_{uuid.uuid4().hex[:8]}",
                "scenario": f"Positive: {tc.get('scenario', '')}",
                "preconditions": tc.get('preconditions', []),
                "steps": tc.get('steps', []),
                "expected_results": tc.get('expected_results', []),
                "test_data": tc.get('test_data', {}),
                "priority": tc.get('priority', 'medium'),
                "module": tc.get('module', 'general'),
                "test_type": "positive"
            }
            positive_tests.append(positive_test)
        return positive_tests

    def _generate_negative_tests(self, test_cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        negative_tests = []
        for tc in test_cases:
            negative_test = {
                "test_id": f"{tc.get('test_id', 'TC')}_NEG_{uuid.uuid4().hex[:8]}",
                "scenario": f"Negative: {tc.get('scenario', '')} with invalid data",
                "preconditions": tc.get('preconditions', []),
                "steps": tc.get('steps', []),
                "expected_results": ["Error message displayed", "Operation rejected"],
                "test_data": {"invalid_input": True},
                "priority": "high",
                "module": tc.get('module', 'general'),
                "test_type": "negative"
            }
            negative_tests.append(negative_test)
        return negative_tests

    def _generate_boundary_tests(self, test_cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        boundary_tests = []
        for tc in test_cases:
            boundary_test = {
                "test_id": f"{tc.get('test_id', 'TC')}_BND_{uuid.uuid4().hex[:8]}",
                "scenario": f"Boundary: {tc.get('scenario', '')} with boundary values",
                "preconditions": tc.get('preconditions', []),
                "steps": tc.get('steps', []),
                "expected_results": tc.get('expected_results', []),
                "test_data": {"boundary_value": True},
                "priority": "medium",
                "module": tc.get('module', 'general'),
                "test_type": "boundary"
            }
            boundary_tests.append(boundary_test)
        return boundary_tests

    def _generate_smoke_tests(self, test_cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [tc for tc in test_cases if tc.get('priority', 'medium').lower() == 'high'][:5]

    def _generate_sanity_tests(self, test_cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [tc for tc in test_cases if tc.get('priority', 'medium').lower() in ['high', 'medium']][:10]

    def _generate_regression_tests(self, test_cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return test_cases
