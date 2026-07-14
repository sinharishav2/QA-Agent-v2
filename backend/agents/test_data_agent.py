from .base_agent import BaseAgent
from typing import Dict, Any, List
import uuid
import random
import string


class TestDataAgent(BaseAgent):
    def __init__(self):
        super().__init__("TestDataAgent")

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            if not self.validate_input(input_data, ['test_cases']):
                raise ValueError("Missing required input fields")

            test_cases = input_data['test_cases']

            valid_data = self._generate_valid_data(test_cases)
            invalid_data = self._generate_invalid_data(test_cases)
            boundary_data = self._generate_boundary_data(test_cases)
            null_data = self._generate_null_data(test_cases)
            random_data = self._generate_random_data(test_cases)
            security_data = self._generate_security_data(test_cases)

            output_data = {
                "valid_data": valid_data,
                "invalid_data": invalid_data,
                "boundary_data": boundary_data,
                "null_data": null_data,
                "random_data": random_data,
                "security_data": security_data,
                "total_datasets": len(valid_data) + len(invalid_data) + len(boundary_data),
                "status": "generated"
            }

            self.log_execution(input_data, output_data, status="success")
            self.logger.info(f"Test data generated: {output_data['total_datasets']} datasets")

            return output_data

        except Exception as e:
            self.logger.error(f"Test data generation failed: {str(e)}")
            output_data = {"error": str(e), "status": "failed"}
            self.log_execution(input_data, output_data, status="failed", error=str(e))
            raise

    def _generate_valid_data(self, test_cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        valid_datasets = []
        for tc in test_cases:
            dataset = {
                "dataset_id": str(uuid.uuid4()),
                "test_id": tc.get('test_id', ''),
                "data_type": "valid",
                "username": "testuser",
                "password": "TestPass123!",
                "email": "test@example.com",
                "phone": "1234567890",
                "address": "123 Test Street",
                "age": 25
            }
            valid_datasets.append(dataset)
        return valid_datasets

    def _generate_invalid_data(self, test_cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        invalid_datasets = []
        for tc in test_cases:
            dataset = {
                "dataset_id": str(uuid.uuid4()),
                "test_id": tc.get('test_id', ''),
                "data_type": "invalid",
                "username": "",
                "password": "123",
                "email": "invalid-email",
                "phone": "abc",
                "address": "",
                "age": -5
            }
            invalid_datasets.append(dataset)
        return invalid_datasets

    def _generate_boundary_data(self, test_cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        boundary_datasets = []
        for tc in test_cases:
            dataset = {
                "dataset_id": str(uuid.uuid4()),
                "test_id": tc.get('test_id', ''),
                "data_type": "boundary",
                "username": "a",
                "password": "P@1",
                "email": "a@b.co",
                "phone": "0",
                "address": "a",
                "age": 0
            }
            boundary_datasets.append(dataset)
        return boundary_datasets

    def _generate_null_data(self, test_cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        null_datasets = []
        for tc in test_cases:
            dataset = {
                "dataset_id": str(uuid.uuid4()),
                "test_id": tc.get('test_id', ''),
                "data_type": "null",
                "username": None,
                "password": None,
                "email": None,
                "phone": None,
                "address": None,
                "age": None
            }
            null_datasets.append(dataset)
        return null_datasets

    def _generate_random_data(self, test_cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        random_datasets = []
        for tc in test_cases:
            dataset = {
                "dataset_id": str(uuid.uuid4()),
                "test_id": tc.get('test_id', ''),
                "data_type": "random",
                "username": ''.join(random.choices(string.ascii_letters, k=8)),
                "password": ''.join(random.choices(string.ascii_letters + string.digits, k=10)),
                "email": f"{''.join(random.choices(string.ascii_lowercase, k=5))}@example.com",
                "phone": ''.join(random.choices(string.digits, k=10)),
                "address": ''.join(random.choices(string.ascii_letters, k=15)),
                "age": random.randint(1, 100)
            }
            random_datasets.append(dataset)
        return random_datasets

    def _generate_security_data(self, test_cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        security_datasets = []
        for tc in test_cases:
            dataset = {
                "dataset_id": str(uuid.uuid4()),
                "test_id": tc.get('test_id', ''),
                "data_type": "security",
                "sql_injection": "'; DROP TABLE users; --",
                "xss_payload": "<script>alert('XSS')</script>",
                "command_injection": "; rm -rf /",
                "path_traversal": "../../etc/passwd",
                "xxe_payload": "<?xml version=\"1.0\"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM \"file:///etc/passwd\">]>"
            }
            security_datasets.append(dataset)
        return security_datasets
