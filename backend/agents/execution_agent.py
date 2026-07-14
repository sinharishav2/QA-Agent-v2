from .base_agent import BaseAgent
from typing import Dict, Any, List
import uuid
from datetime import datetime


class ExecutionAgent(BaseAgent):
    def __init__(self):
        super().__init__("ExecutionAgent")
        self.supported_browsers = ["chrome", "firefox", "edge", "safari"]
        self.execution_modes = ["sequential", "parallel"]

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            if not self.validate_input(input_data, ['test_cases', 'project_id']):
                raise ValueError("Missing required input fields")

            project_id = input_data['project_id']
            test_cases = input_data['test_cases']
            browser = input_data.get('browser', 'chrome')
            execution_mode = input_data.get('execution_mode', 'sequential')

            execution_results = self._execute_tests(test_cases, browser, execution_mode)

            output_data = {
                "project_id": project_id,
                "execution_results": execution_results,
                "total_tests": len(test_cases),
                "passed": len([r for r in execution_results if r['status'] == 'passed']),
                "failed": len([r for r in execution_results if r['status'] == 'failed']),
                "skipped": len([r for r in execution_results if r['status'] == 'skipped']),
                "status": "completed"
            }

            self.log_execution(input_data, output_data, status="success")
            self.logger.info(f"Test execution completed: {output_data['passed']} passed, {output_data['failed']} failed")

            return output_data

        except Exception as e:
            self.logger.error(f"Test execution failed: {str(e)}")
            output_data = {"error": str(e), "status": "failed"}
            self.log_execution(input_data, output_data, status="failed", error=str(e))
            raise

    def _execute_tests(self, test_cases: List[Dict[str, Any]], browser: str, mode: str) -> List[Dict[str, Any]]:
        results = []

        for test_case in test_cases:
            result = {
                "test_id": test_case.get('test_id', str(uuid.uuid4())),
                "scenario": test_case.get('scenario', ''),
                "status": self._simulate_test_execution(),
                "execution_time": self._simulate_execution_time(),
                "screenshots": self._generate_screenshot_paths(),
                "logs": self._generate_log_entries(),
                "console_errors": [],
                "network_logs": [],
                "timestamp": datetime.utcnow().isoformat()
            }
            results.append(result)

        return results

    def _simulate_test_execution(self) -> str:
        import random
        return random.choice(["passed", "failed", "skipped"])

    def _simulate_execution_time(self) -> float:
        import random
        return round(random.uniform(0.5, 5.0), 2)

    def _generate_screenshot_paths(self) -> List[str]:
        return [
            f"/screenshots/test_{uuid.uuid4().hex[:8]}.png",
            f"/screenshots/test_{uuid.uuid4().hex[:8]}_error.png"
        ]

    def _generate_log_entries(self) -> List[str]:
        return [
            "Test started",
            "Navigating to application",
            "Entering credentials",
            "Clicking login button",
            "Verifying dashboard",
            "Test completed"
        ]
